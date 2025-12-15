# app/main.py
from fastapi import FastAPI, Request
from uuid import uuid4
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from app.core.errors import AppError, ErrorCode

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

"""
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = rid

    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


def _err_response(request: Request, *, status_code: int, error: str, message: str, www_auth: str | None = None):
    headers = {"Cache-Control": "no-store"}
    if www_auth:
        headers["WWW-Authenticate"] = www_auth
    return JSONResponse(
        status_code=status_code,
        headers=headers,
        content={
            "error": error,
            "message": message,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return _err_response(
        request,
        status_code=exc.status_code,
        error=exc.error,
        message=exc.message,
        www_auth=exc.www_authenticate,
    )


# "/없는경로" 같은 프레임워크 404도 스샷 포맷으로
@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return _err_response(
            request,
            status_code=404,
            error=ErrorCode.RESOURCE_NOT_FOUND.value,
            message="요청한 리소스를 찾을 수 없습니다.",
        )
    # 혹시 415가 프레임워크에서 오면 통일
    if exc.status_code == 415:
        return _err_response(
            request,
            status_code=415,
            error=ErrorCode.UNSUPPORTED_MEDIA_TYPE.value,
            message="요청은 'multipart/form-data'여야 하며, 이미지 파트는 'image/*'여야 합니다.",
        )
    # 그 외는 필요하면 정책대로 확장
    return _err_response(
        request,
        status_code=exc.status_code,
        error="http_error",
        message=str(exc.detail) if isinstance(exc.detail, str) else "요청 처리 중 오류가 발생했습니다.",
    )


# (선택) FastAPI validation 에러도 포맷 통일하고 싶으면
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return _err_response(
        request,
        status_code=400,  # 너희 정책이 400이면 400, 아니면 422로
        error="bad_request",
        message="요청 값이 올바르지 않습니다.",
    )


# 500도 스샷 포맷으로
@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    return _err_response(
        request,
        status_code=500,
        error=ErrorCode.INTERNAL_SERVER_ERROR.value,
        message="서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
    )
    """