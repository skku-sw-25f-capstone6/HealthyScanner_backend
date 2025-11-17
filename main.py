from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")


@app.get("/auth/kakao/login")
def login():
    kakao_auth_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
        f"&response_type=code"
    )
    return RedirectResponse(kakao_auth_url)


@app.get("/auth/kakao/callback")
def kakao_callback(code: str):
    # 토큰 요청
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

    # 사용자 정보 요청
    user_info = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    user_id = user_info.get("id")

    jwt_token = f"dummy-jwt-for-{user_id}"

    # ⭐ body 내부에는 JSON 문자열만 있어야 한다!
    html = f"""
    <html>
      <body>
        {{ "jwt": "{jwt_token}", "user_id": "{user_id}" }}
      </body>
    </html>
    """

    return HTMLResponse(html)
