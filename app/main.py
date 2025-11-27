# app/main.py
from fastapi import FastAPI
from app.routers import (
    user_router,
    product_router,
    ingredient_router,
    nutrition_router,
    scan_history_router,
    user_daily_score_router,
    mypage_router,
    me_router,
    auth_router,
    auth_user_router,
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
