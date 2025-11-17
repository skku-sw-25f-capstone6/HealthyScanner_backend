from fastapi import FastAPI
from routers.auth_router import router as auth_router

app = FastAPI()

# 라우터 등록
app.include_router(auth_router)
