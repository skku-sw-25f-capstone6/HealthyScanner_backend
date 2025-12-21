from urllib import request
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from uuid import uuid4
from app.core.database import get_db
from app.models.user import User
from app.core.auth import create_access_token, get_current_user, create_app_refresh_token
from fastapi import Request
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

from fastapi.responses import JSONResponse
from sqlalchemy import text


from pydantic import BaseModel

load_dotenv()
router = APIRouter()

# ---------------------------------------------------------
# 🔥 Kakao OAuth Config
# ---------------------------------------------------------
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI_IOS = os.getenv("KAKAO_REDIRECT_URI_IOS")
KAKAO_REDIRECT_URI_ANDROID = os.getenv("KAKAO_REDIRECT_URI_ANDROID")
KAKAO_REDIRECT_URI_LOCAL = "http://127.0.0.1:8000/auth/kakao/callback"


# ---------------------------------------------------------
# 1️⃣ Kakao Login Redirect
# ---------------------------------------------------------
@router.get("/auth/kakao/login")
def kakao_login(platform: str = Query("ios")):
    if platform == "android":
        redirect_uri = KAKAO_REDIRECT_URI_ANDROID
    elif platform == "local":
        redirect_uri = KAKAO_REDIRECT_URI_LOCAL
    else:
        redirect_uri = KAKAO_REDIRECT_URI_IOS

    kakao_auth_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&state={platform}"
    )

    return RedirectResponse(kakao_auth_url)


# ---------------------------------------------------------
# 2️⃣ Kakao Callback + App Token Issuance
# ---------------------------------------------------------
@router.get("/auth/kakao/callback")
def kakao_callback(
    code: str,
    state: str = Query("ios"),
    db: Session = Depends(get_db),
):
    # 플랫폼별 redirect_uri
    if state == "android":
        redirect_uri = KAKAO_REDIRECT_URI_ANDROID
    elif state == "local":
        redirect_uri = KAKAO_REDIRECT_URI_LOCAL
    else:
        redirect_uri = KAKAO_REDIRECT_URI_IOS

    # -------------------------------------------------
    # Step 1) Kakao Access Token 요청
    # -------------------------------------------------
    token_res = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": KAKAO_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "code": code,
        },
    ).json()

    kakao_access_token = token_res.get("access_token")
    if not kakao_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get Kakao access token",
        )

    kakao_refresh_token = token_res.get("refresh_token")
    token_type = token_res.get("token_type")
    expires_in = token_res.get("expires_in")
    refresh_expires_in = token_res.get("refresh_token_expires_in")

    # -------------------------------------------------
    # Step 2) Kakao User Info
    # -------------------------------------------------
    user_info = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {kakao_access_token}"},
    ).json()

    kakao_user_id = str(user_info.get("id"))
    nickname = (
        user_info.get("kakao_account", {})
        .get("profile", {})
        .get("nickname")
    )
    profile_image = (
        user_info.get("kakao_account", {})
        .get("profile", {})
        .get("profile_image_url")
    )

    # -------------------------------------------------
    # Step 3) User Upsert
    # -------------------------------------------------
    user = db.query(User).filter(User.kakao_user_id == kakao_user_id, User.deleted_at.is_(None),).first()

    if not user:
        user = User(
            id=str(uuid4()),
            kakao_user_id=kakao_user_id,
            name=nickname,
            profile_image_url=profile_image,
            created_at=datetime.utcnow(),
        )
        db.add(user)

    # Kakao token 저장
    user.access_token = kakao_access_token
    user.refresh_token = kakao_refresh_token
    user.token_type = token_type
    user.expires_in = expires_in
    user.refresh_expires_in = refresh_expires_in

    # -------------------------------------------------
    # 🔐 App Token Issuance
    # -------------------------------------------------
    app_access_token = create_access_token(user.id)
    app_refresh_token = create_app_refresh_token()

    user.app_refresh_token = app_refresh_token

    db.commit()
    db.refresh(user)

    # -------------------------------------------------
    # ✅ Redirect + Cookie (여기가 핵심)
    # -------------------------------------------------
    response = JSONResponse({
      "app_access_token": app_access_token,
      "app_refresh_token": app_refresh_token,

      # (필요하면 그대로 유지)
      "kakao_access_token": kakao_access_token,
      "kakao_refresh_token": kakao_refresh_token,
      "token_type": token_type,
      "expires_in": expires_in,
      "refresh_expires_in": refresh_expires_in,
      "kakao_user_id" : kakao_user_id,
      "user_id": user.id,
    })

    
    return response


# ---------------------------------------------------------
# 3️⃣ Get Current User
# ---------------------------------------------------------
@router.get("/auth/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "profile_image_url": user.profile_image_url,
    }


# ---------------------------------------------------------
# 4️⃣ Logout (Invalidate Refresh Token)
# ---------------------------------------------------------
@router.post("/auth/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
):
    token = request.headers.get("Authorization")
    if not token:
        return {"message": "Already logged out.(No Token Found)"}

    try:
        user = get_current_user(request, db=db)
    except Exception:
        return {"message": "already logged out"}

    user.app_refresh_token = None
    user.access_token = None
    user.refresh_token = None
    user.token_type = None
    user.expires_in = None
    user.refresh_expires_in = None
    db.commit()

    return {"message": "logout 성공!"}


# ---------------------------------------------------------
# 5️⃣ Unlink Kakao Account
# ---------------------------------------------------------
@router.delete("/auth/unlink")
def unlink_account(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    KAKAO_ADMIN_KEY = os.getenv("KAKAO_ADMIN_KEY")
    if not KAKAO_ADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="KAKAO_ADMIN_KEY not configured",
        )

    kakao_res = requests.post(
        "https://kapi.kakao.com/v1/user/unlink",
        headers={
            "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "target_id_type": "user_id",
            "target_id": user.kakao_user_id,  # 카카오 user_id
        },
        timeout=5,
    )

    if kakao_res.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to unlink Kakao account",
        )

    db.execute(
        text("DELETE FROM user_daily_score WHERE user_id = :uid"),
        {"uid": user.id},
    )
    db.execute(
        text("DELETE FROM scan_history WHERE user_id = :uid"),
        {"uid": user.id},
    )
    
    db.execute(
        text("DELETE FROM user WHERE id = :uid"),
        {"uid": user.id},
    )

    db.commit()
    return {"message": "account unlinked"}


# ---------------------------------------------------------
# 📌 Refresh Token Request Schema
# ---------------------------------------------------------
class RefreshTokenRequest(BaseModel):
    app_refresh_token: str


# ---------------------------------------------------------
# 6️⃣ Refresh Access Token
# ---------------------------------------------------------
@router.post("/v1/auth/refresh")
def refresh_access_token(
    body: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    refresh_token = body.app_refresh_token

    # 🔍 Refresh Token으로 사용자 조회
    user = (
        db.query(User)
        .filter(User.app_refresh_token == refresh_token)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # 🔐 새 Access Token 발급
    new_access_token = create_access_token(user.id)

    return {
        "app_access_token": new_access_token
    }
