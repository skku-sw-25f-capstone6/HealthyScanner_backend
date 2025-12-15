# app/core/auth.py
from datetime import datetime, timedelta
from typing import Optional
import secrets
import jwt  # PyJWT (requirements.txt에 pyjwt 추가 필요)
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.DAL.user_DAL import UserDAL
from app.models.user import User  # ORM User 모델

# TODO: 나중에 .env / settings로 빼기
SECRET_KEY = "CHANGE_ME_TO_A_LONG_RANDOM_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60   # 1시간으로 변경

bearer_scheme = HTTPBearer(auto_error=True)


def create_access_token(
    user_id: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    우리 서버에서 쓰는 Access Token(JWT) 발급용 함수.
    payload의 sub에 user_id를 넣는 패턴.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + expires_delta,
    }

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    JWT를 디코드하고, 유효하지 않으면 HTTP 401을 던진다.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Depends(get_current_user)를 쓰는 라우터는
    - Authorization: Bearer <우리 JWT> 헤더를 요구하게 됨
    - JWT에서 user_id(sub)를 꺼내서 DB에서 User를 찾아 반환

    라우터 입장에서는 'current_user: User'만 받으면 되고,
    JWT 파싱/검증은 전혀 몰라도 됨.
    """
    token = credentials.credentials  # "Bearer xxx" 중 xxx 부분

    payload = decode_access_token(token)
    user_id: Optional[str] = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = UserDAL.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user

def create_app_refresh_token() -> str:
    """
    우리 서비스용 Refresh Token
    """
    return secrets.token_urlsafe(64)