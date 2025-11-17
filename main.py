from fastapi import FastAPI
from routers.auth_router import router as auth_router
from routers.auth_user_router import router as auth_user_router
from app.core.database import Base, engine
from app.models.user import User

app = FastAPI()

# 라우터 등록
app.include_router(auth_router)
app.include_router(auth_user_router)
Base.metadata.create_all(bind=engine)