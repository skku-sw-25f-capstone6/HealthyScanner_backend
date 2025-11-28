CREATE TABLE user (
    id TEXT PRIMARY KEY,                             -- UUID v4 권장
    name TEXT,

    habits     JSON,                                 -- JSON 문자열
    conditions JSON,                                 -- JSON 문자열 (원하면 json_valid 체크 추가 가능)
    allergies  JSON,                                 -- JSON 문자열
    -- scan_count INTEGER DEFAULT 0,                    -- 이건 나중에 너무 불편하다 싶으면 풀자
    
    profile_image_url TEXT,

      -- 🔐 카카오 로그인용 인증 정보
    access_token TEXT,                    -- 카카오 access_token
    refresh_token TEXT,                   -- 카카오 refresh_token
    token_type VARCHAR(50),               -- 보통 'bearer'
    expires_in INT,                       useruser-- access_token 유효기간(초)
    refresh_expires_in INT,               -- refresh_token 유효기간(초)
    
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    deleted_at DATETIME(6) NULL
);
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;