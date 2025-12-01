CREATE TABLE user (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),

    habits JSON,
    conditions JSON,
    allergies JSON,

    profile_image_url TEXT,

    access_token TEXT,
    refresh_token TEXT,
    token_type VARCHAR(50),
    expires_in INT,
    refresh_expires_in INT,

    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    deleted_at DATETIME(6)
)
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
