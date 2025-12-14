# app/core/errors.py
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class ErrorCode(str, Enum):
    # 400
    MISSING_BARCODE = "missing_barcode"

    # 401
    MISSING_TOKEN = "missing_token"
    MALFORMED_TOKEN = "malformed_token"

    # 404
    RESOURCE_NOT_FOUND = "resource_not_found"

    # 415
    UNSUPPORTED_MEDIA_TYPE = "unsupported_media_type"

    # 500
    INTERNAL_SERVER_ERROR = "internal_server_error"


@dataclass(frozen=True)
class ErrorSpec:
    status_code: int
    message: str
    www_authenticate: Optional[str] = None  # 401에서만 사용


ERROR_SPECS: dict[ErrorCode, ErrorSpec] = {
    ErrorCode.MISSING_BARCODE: ErrorSpec(
        400,
        "바코드 정보가 누락되었습니다.",
    ),
    ErrorCode.MISSING_TOKEN: ErrorSpec(
        401,
        "Authorization 헤더가 없습니다.",
        'Bearer error="missing_token", error_description="The access token is missing."',
    ),
    ErrorCode.MALFORMED_TOKEN: ErrorSpec(
        401,
        "Authorization 헤더 형식이 잘못되었습니다.",
        'Bearer error="malformed_token", error_description="The access token is malformed."',
    ),
    ErrorCode.RESOURCE_NOT_FOUND: ErrorSpec(
        404,
        "요청한 리소스를 찾을 수 없습니다.",
    ),
    ErrorCode.UNSUPPORTED_MEDIA_TYPE: ErrorSpec(
        415,
        "요청은 'multipart/form-data'여야 하며, 이미지 파트는 'image/*'여야 합니다.",
    ),
    ErrorCode.INTERNAL_SERVER_ERROR: ErrorSpec(
        500,
        "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
    ),
}


class AppError(Exception):
    def __init__(self, code: ErrorCode, *, detail: Any | None = None, override_message: str | None = None):
        spec = ERROR_SPECS.get(code, ERROR_SPECS[ErrorCode.INTERNAL_SERVER_ERROR])
        self.code: ErrorCode = code
        self.status_code: int = spec.status_code
        self.message: str = override_message or spec.message
        self.www_authenticate: Optional[str] = spec.www_authenticate
        self.detail: Any | None = detail  # 필요하면 로그/디버그용
        super().__init__(self.message)

    @property
    def error(self) -> str:
        return self.code.value
