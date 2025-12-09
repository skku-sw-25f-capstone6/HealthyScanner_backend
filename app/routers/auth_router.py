from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
#from utils.jwt_handler import create_jwt
from app.core.auth import create_access_token, get_current_user
#from utils.auth_dependency import get_current_user

import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# 🔥 카카오 REST API 설정
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI_IOS = os.getenv("KAKAO_REDIRECT_URI_IOS")
KAKAO_REDIRECT_URI_ANDROID = os.getenv("KAKAO_REDIRECT_URI_ANDROID")
KAKAO_REDIRECT_URI_LOCAL = "http://127.0.0.1:8000/auth/kakao/callback"


# ————————————————————————————————————
# 📌 1) 카카오 로그인 URL 리다이렉트
# ————————————————————————————————————
@router.get("/auth/kakao/login")
def login(platform: str = Query("ios")):
    if platform == "android":
        redirect_uri = f"{KAKAO_REDIRECT_URI_ANDROID}?platform=android"
    elif platform == "local":
        redirect_uri = f"{KAKAO_REDIRECT_URI_LOCAL}?platform=local"
    else:
        redirect_uri = f"{KAKAO_REDIRECT_URI_IOS}?platform=ios"

    kakao_auth_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
    )

    return RedirectResponse(kakao_auth_url)


# ————————————————————————————————————
# 📌 2) 카카오 콜백 처리 + 자동 회원가입
# ————————————————————————————————————
@router.get("/auth/kakao/callback")
def kakao_callback(
    code: str,
    platform: str = Query("ios"),
    db: Session = Depends(get_db),
):
    # 플랫폼별 리다이렉트 URI 매칭
    if platform == "android":
        redirect_uri = f"{KAKAO_REDIRECT_URI_ANDROID}?platform=android"
    elif platform == "local":
        redirect_uri = f"{KAKAO_REDIRECT_URI_LOCAL}?platform=local"
    else:
        redirect_uri = f"{KAKAO_REDIRECT_URI_IOS}?platform=ios"

    # -------------------------
    # 🔥 step 1) access token 요청
    # -------------------------
    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "code": code,
    }

    token_res = requests.post(token_url, data=data).json()
    access_token = token_res.get("access_token")

    if not access_token:
        return {"error": "token_failed"}

    refresh_token = token_res.get("refresh_token")
    token_type = token_res.get("token_type")
    expires_in = token_res.get("expires_in")
    refresh_expires_in = token_res.get("refresh_token_expires_in")

    # -------------------------
    # 🔥 step 2) 사용자 정보 요청
    # -------------------------
    user_info = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    kakao_user_id = str(user_info.get("id"))
    nickname = user_info.get("kakao_account", {}).get("profile", {}).get("nickname")
    profile_image = user_info.get("kakao_account", {}).get("profile", {}).get("profile_image_url")

    # -------------------------
    # 🔥 step 3) DB 사용자 조회
    # -------------------------
    user = db.query(User).filter(User.id == kakao_user_id).first()

    if not user:
        # 🔥 최초 가입
        user = User(
            id=kakao_user_id,
            name=nickname,
            profile_image_url=profile_image,

            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
            expires_in=expires_in,
            refresh_expires_in=refresh_expires_in,

            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"🆕 신규 회원 생성: {kakao_user_id}")

    else:
        # 🔄 기존 회원 업데이트
        print(f"✔ 기존 회원 로그인: {kakao_user_id}")

        user.name = nickname
        user.profile_image_url = profile_image
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.token_type = token_type
        user.expires_in = expires_in
        user.refresh_expires_in = refresh_expires_in

        db.commit()
        db.refresh(user)

    # ---------------------------------------------------------
    # 🔥 step 5) JWT 발급
    # ---------------------------------------------------------
    jwt_token = create_access_token(kakao_user_id)

    # ---------------------------------------------------------
    # 🟦 최종 JSON 응답 11/30 수정 사항 반영 - content type JSON 수정 반영 (Flutter 용)
    # ---------------------------------------------------------
    return {
        "access_token": jwt_token,              # ← 이제 이게 “우리 JWT”
        "token_type": "bearer",

        "kakao_access_token": access_token,     # ← Kakao 토큰은 이름을 분리
        "kakao_refresh_token": refresh_token,
        "kakao_expires_in": expires_in,
        "kakao_refresh_expires_in": refresh_expires_in,
    }


# ————————————————————————————————————
# 📌 3) 로그인 후 사용자 정보 조회
# ————————————————————————————————————
@router.get("/auth/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "profile_image_url": user.profile_image_url,
        "access_token": user.access_token,
        "refresh_token": user.refresh_token,
        "token_type": user.token_type,
        "expires_in": user.expires_in,
        "refresh_expires_in": user.refresh_expires_in,
    }


# ————————————————————————————————————
# 📌 4~8) 나머지 기능은 그대로 유지
# ————————————————————————————————————

def is_access_token_valid(access_token: str) -> bool:
    url = "https://kapi.kakao.com/v1/user/access_token_info"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.status_code == 200


def refresh_kakao_access_token(refresh_token: str):
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": KAKAO_CLIENT_ID,
        "refresh_token": refresh_token,
    }

    res = requests.post(url, data=data)

    if res.status_code != 200:
        return None

    return res.json()


def ensure_valid_kakao_access_token(user: User, db: Session):
    if is_access_token_valid(user.access_token):
        return user.access_token

    print("⛔ Access Token 만료됨 → Refresh Token으로 재발급 시도")

    refreshed = refresh_kakao_access_token(user.refresh_token)

    if not refreshed or "access_token" not in refreshed:
        print("❌ Refresh Token도 만료됨 → 재로그인 필요")
        return None

    user.access_token = refreshed["access_token"]
    user.expires_in = refreshed.get("expires_in")

    if refreshed.get("refresh_token"):
        user.refresh_token = refreshed["refresh_token"]
        user.refresh_expires_in = refreshed.get("refresh_token_expires_in")

    db.commit()
    db.refresh(user)

    print("🔄 Access Token 자동 갱신 완료!")
    return user.access_token


@router.post("/auth/logout")
def logout(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user.refresh_token = None
    user.access_token = None
    user.expires_in = None
    user.refresh_expires_in = None
    user.token_type = None

    db.commit()
    db.refresh(user)

    return {"message": "logout success"}


@router.delete("/auth/unlink")
def unlink_account(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kakao_unlink_url = "https://kapi.kakao.com/v1/user/unlink"
    headers = {
        "Authorization": f"Bearer {user.access_token}"
    }

    kakao_res = requests.post(kakao_unlink_url, headers=headers)

    if kakao_res.status_code != 200:
        print("❌ 카카오 unlink 실패:", kakao_res.text)
        raise HTTPException(
            status_code=400,
            detail="Failed to unlink Kakao account"
        )

    print(f"🔗 카카오 unlink 성공: {user.id}")

    user.access_token = None
    user.refresh_token = None
    user.token_type = None
    user.expires_in = None
    user.refresh_expires_in = None
    user.deleted_at = datetime.utcnow()

    db.commit()

    return {
        "status": "success",
        "message": "Account unlinked and deleted"
    }
