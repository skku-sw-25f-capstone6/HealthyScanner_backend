from datetime import datetime, timedelta
from typing import Optional
import secrets
import jwt  # PyJWT (requirements.txt에 pyjwt 추가 필요)
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.DAL.user_DAL import UserDAL
from app.models.user import User  # ORM User 모델

# TODO: 나중에 .env / settings로 빼기
SECRET_KEY = "CHANGE_ME_TO_A_LONG_RANDOM_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60   # 1시간으로 변경
ACCESS_TOKEN_EXPIRE_MINUTES = 60   # 1시간으로 변경

bearer_scheme = HTTPBearer(auto_error=True)
security = HTTPBearer(auto_error=False)

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

    now = datetime.now()
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + expires_delta,
    }

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        # leeway=10을 추가하여 10초 정도의 시간 차이는 허용합니다.
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            leeway=10  # 시간 오차 허용 범위 추가
        )
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
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = None

    # 1) Authorization: Bearer <token>
    if creds and creds.scheme.lower() == "bearer":
        token = creds.credentials

    # 2) (옵션) 쿠키 fallback도 유지하고 싶다면
    if not token:
        token = request.cookies.get("access_token")
    

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = decode_access_token(token)
    user_id = payload.get("sub")

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
