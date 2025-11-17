# app/routers/auth_router.py

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from utils.jwt_handler import create_jwt

import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")


# -------------------------------------------------------------------------
#  1) 카카오 로그인 URL 리다이렉트
# -------------------------------------------------------------------------
@router.get("/auth/kakao/login")
def login():
    kakao_auth_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
        f"&response_type=code"
    )
    return RedirectResponse(kakao_auth_url)


# -------------------------------------------------------------------------
#  2) 카카오 콜백 처리 + 자동 회원가입 (SQLAlchemy)
# -------------------------------------------------------------------------
@router.get("/auth/kakao/callback")
def kakao_callback(code: str, db: Session = Depends(get_db)):

    # -------------------------
    #  step 1) access token 요청
    # -------------------------
    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code,
    }

    token_res = requests.post(token_url, data=data).json()
    access_token = token_res.get("access_token")

    if not access_token:
        return HTMLResponse("<body>{\"error\": \"token_failed\"}</body>")

    # -------------------------
    #  step 2) 사용자 정보 요청
    # -------------------------
    user_info = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    kakao_user_id = str(user_info.get("id"))
    nickname = user_info.get("kakao_account", {}) \
                        .get("profile", {}) \
                        .get("nickname")
    profile_image = user_info.get("kakao_account", {}) \
                              .get("profile", {}) \
                              .get("profile_image_url")

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
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"🆕 신규 회원 생성: {kakao_user_id}")
    else:
        print(f"✔ 기존 회원 로그인: {kakao_user_id}")

    # ---------------------------------------------------------------------
    #  step 5) JWT 생성
    # ---------------------------------------------------------------------
    jwt_token = create_jwt(kakao_user_id)

    html = f"""
    <html>
      <body>
        {{ "jwt": "{jwt_token}", "user_id": "{kakao_user_id}" }}
      </body>
    </html>
    """

    return HTMLResponse(html)