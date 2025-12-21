# app/main.py
from fastapi import FastAPI, Request
from uuid import uuid4
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from app.core.errors import AppError, ErrorCode
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.routers import (
    user_router,
    product_router,
    ingredient_router,
    nutrition_router,
    scan_history_router,
    scan_flow_router,
    user_daily_score_router,
    mypage_router,
    me_router,
    auth_router,
    auth_user_router,
    home_router,
)

from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HealthyScanner Backend", version="0.1.0")


app.include_router(user_router.router)
app.include_router(product_router.router)
app.include_router(nutrition_router.router)
app.include_router(ingredient_router.router)
app.include_router(scan_history_router.router)
app.include_router(user_daily_score_router.router)
app.include_router(mypage_router.router)
app.include_router(me_router.router)    
app.include_router(auth_router.router)
app.include_router(auth_user_router.router)
app.include_router(scan_flow_router.router)
app.include_router(home_router.router)



@app.get("/")
def root():
    return JSONResponse({
        "message": "HealthyScanner backend running"
    })


#사진 가져오는 메서드

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)