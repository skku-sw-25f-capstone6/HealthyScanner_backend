CREATE TABLE scan_history (
    id CHAR(36) PRIMARY KEY,                  -- 스캔 기록 UUID
    user_id CHAR(36) NOT NULL,
    product_id CHAR(36) NULL,

    scanned_at DATETIME(6) NOT NULL,          -- 스캔 시각

    display_name VARCHAR(256),                -- 사용자가 지정한 제품명
    display_category VARCHAR(128),            -- 사용자가 지정한 카테고리
    image_url TEXT,                           -- 제품 이미지 URL

    decision ENUM('avoid','caution','ok'),    -- NULL 허용(아직 분석 전 등)

    summary VARCHAR(255),                     -- 예: "당류 25g/회 → 고당"
    ai_total_score TINYINT UNSIGNED,          -- 0~100 (0~33 나쁨, 34~66 보통, 67~100 좋음)

    conditions JSON,                          -- ["diabetes", ...]
    allergies  JSON,                          -- ["peanut", ...]
    habits     JSON,                          -- ["low_sugar", ...]

    ai_allergy_report   TEXT,
    ai_condition_report TEXT,
    ai_alter_report     TEXT,
    ai_vegan_report     TEXT,
    ai_total_report     TEXT,

    caution_factors JSON,

    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),
    deleted_at DATETIME(6) NULL,

    CONSTRAINT fk_scan_history_user
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    CONSTRAINT fk_scan_history_product
        FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
)
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;
