from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from utils.jwt_handler import create_jwt
from utils.auth_dependency import get_current_user      # ⭐ 추가됨

import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI_IOS = os.getenv("KAKAO_REDIRECT_URI_IOS")
KAKAO_REDIRECT_URI_ANDROID = os.getenv("KAKAO_REDIRECT_URI_ANDROID")

# ————————————————————————————————————
#  1) 카카오 로그인 URL 리다이렉트
# ————————————————————————————————————
@router.get("/auth/kakao/login")
def login(platform: str = Query("ios")):
    if platform == "android":
        redirect_uri = f"{KAKAO_REDIRECT_URI_ANDROID}?platform=android"
    else:
        redirect_uri = f"{KAKAO_REDIRECT_URI_IOS}?platform=ios"

    kakao_auth_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
    )
    return RedirectResponse(kakao_auth_url)


# -------------------------------------------------------------------------
#  2) 카카오 콜백 처리 + 자동 회원가입 (SQLAlchemy)
# -------------------------------------------------------------------------
@router.get("/auth/kakao/callback")
def kakao_callback(
    code: str,
    platform: str = Query("ios"),
    db: Session = Depends(get_db),
):
    if platform == "android":
        redirect_uri = f"{KAKAO_REDIRECT_URI_ANDROID}?platform=android"
    else:
        redirect_uri = f"{KAKAO_REDIRECT_URI_IOS}?platform=ios"
    
    # -------------------------
    #  step 1) access token 요청
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
        return HTMLResponse("<body>{\"error\": \"token_failed\"}</body>")

    # 🔥 카카오 토큰 값 추출
    refresh_token = token_res.get("refresh_token")
    token_type = token_res.get("token_type")
    expires_in = token_res.get("expires_in")
    refresh_expires_in = token_res.get("refresh_token_expires_in")

    # -------------------------
    #  step 2) 사용자 정보 요청
    # -------------------------
    user_info = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    kakao_user_id = str(user_info.get("id"))
    nickname = user_info.get("kakao_account", {}).get("profile", {}).get("nickname")
    profile_image = user_info.get("kakao_account", {}).get("profile", {}).get("profile_image_url")

    # ---------------------------------------------------------------------
    #  step 3) DB에서 사용자 조회
    # ---------------------------------------------------------------------
    user = db.query(User).filter(User.id == kakao_user_id).first()

    if not user:
        # -----------------------------------------------------------------
        #  step 4) 최초 회원가입
        # -----------------------------------------------------------------
        user = User(
            id=kakao_user_id,
            name=nickname,
            profile_image_url=profile_image,

            # 🔥 카카오 토큰 저장
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
        print(f"✔ 기존 회원 로그인: {kakao_user_id}")

        # 🔥 기존 사용자 업데이트 (항상 최신 정보 유지)
        user.name = nickname
        user.profile_image_url = profile_image

        user.access_token = access_token
        user.refresh_token = refresh_token
        user.token_type = token_type
        user.expires_in = expires_in
        user.refresh_expires_in = refresh_expires_in

        db.commit()

    # ---------------------------------------------------------------------
    #  step 5) JWT 생성
    # ---------------------------------------------------------------------
    jwt_token = create_jwt(kakao_user_id)

    html = f"""
<html>
  <body>
    <script>
      window.onload = function() {{
        kakaoLogin.postMessage(JSON.stringify({{
          "jwt": "{jwt_token}",
          "user_id": "{kakao_user_id}"
        }}));
      }};
    </script>
  </body>
</html>
"""
    return HTMLResponse(html)



# -------------------------------------------------------------------------
#  3) 로그인 후 사용자 정보 조회 (/auth/me)
# -------------------------------------------------------------------------
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



# -------------------------------------------------------------
#  🟦 Step 1) Access Token 유효성 검사 함수
# -------------------------------------------------------------
def is_access_token_valid(access_token: str) -> bool:
    url = "https://kapi.kakao.com/v1/user/access_token_info"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.status_code == 200



# -------------------------------------------------------------
#  🟩 Step 2) Refresh Token으로 Access Token 재발급 함수
# -------------------------------------------------------------
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



# -------------------------------------------------------------
#  🟧 Step 3) Access Token 자동 갱신 통합 함수
# -------------------------------------------------------------
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



# -------------------------------------------------------------------------
#  4) 로그아웃 (/auth/logout)
# -------------------------------------------------------------------------
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

# -------------------------------------------------------------------------
#  5) 카카오 계정 연결 해제(회원 탈퇴)
# -------------------------------------------------------------------------
@router.delete("/auth/unlink")
def unlink_account(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    - 현재 로그인한 유저의 Kakao 계정을 unlink (서비스 연결 끊기)
    - DB에서 refresh_token 삭제
    - DB에서 유저 계정 soft-delete 또는 hard-delete
    """

    # Step 1) 카카오 unlink API 호출
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

    # Step 2) DB 토큰 제거
    user.access_token = None
    user.refresh_token = None
    user.token_type = None
    user.expires_in = None
    user.refresh_expires_in = None

    # Step 3) 유저 삭제(soft delete)
    # 강제 삭제하고 싶으면 db.delete(user)
    user.deleted_at = datetime.utcnow()

    db.commit()

    return {
        "status": "success",
        "message": "Account unlinked and deleted"
    }
