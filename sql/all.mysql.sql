CREATE TABLE user (
    id CHAR(36) PRIMARY KEY,                             -- UUID v4 권장
    name VARCHAR(100),

    habits     JSON,                                 -- JSON 문자열
    conditions JSON,                                 -- JSON 문자열 (원하면 json_valid 체크 추가 가능)
    allergies  JSON,                                 -- JSON 문자열
    -- scan_count INTEGER DEFAULT 0,                    -- 이건 나중에 너무 불편하다 싶으면 풀자
    
    profile_image_url TEXT,

      -- 🔐 카카오 로그인용 인증 정보
    access_token TEXT,                    -- 카카오 access_token
    refresh_token TEXT,                   -- 카카오 refresh_token
    token_type VARCHAR(50),               -- 보통 'bearer'
    expires_in INT,                       -- access_token 유효기간(초)
    refresh_expires_in INT,               -- refresh_token 유효기간(초)
    
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    deleted_at DATETIME(6) NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE product (
    id CHAR(36) PRIMARY KEY,        -- 제품 고유 UUID

    barcode VARCHAR(32) UNIQUE,     -- EAN/UPC/Code128
    barcode_kind VARCHAR(16),       -- 'EAN13'|'UPC'|'CODE128'
    brand VARCHAR(128),
    name VARCHAR(256),
    category VARCHAR(128),
    size_text VARCHAR(64),
    image_url TEXT,
    country VARCHAR(64),
    notes TEXT,
    score INTEGER,

    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),

    CHECK (
        barcode IS NULL OR
        (barcode REGEXP '^[0-9]{8}$'
         OR barcode REGEXP '^[0-9]{12}$'
         OR barcode REGEXP '^[0-9]{13}$'
         OR barcode REGEXP '^[0-9]{14}$')
    )
)
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE TABLE nutrition (
    id CHAR(36) PRIMARY KEY,                  -- 서버가 관리하는 nutrition UUID
    product_id CHAR(36) NOT NULL,             -- product.id(FK)

    per_serving_grams DOUBLE CHECK (per_serving_grams IS NULL OR per_serving_grams > 0),
    calories        DOUBLE CHECK (calories      IS NULL OR calories      >= 0),
    carbs_g         DOUBLE CHECK (carbs_g       IS NULL OR carbs_g       >= 0),
    sugar_g         DOUBLE CHECK (sugar_g       IS NULL OR sugar_g       >= 0),
    protein_g       DOUBLE CHECK (protein_g     IS NULL OR protein_g     >= 0),
    fat_g           DOUBLE CHECK (fat_g         IS NULL OR fat_g         >= 0),
    sat_fat_g       DOUBLE CHECK (sat_fat_g     IS NULL OR sat_fat_g     >= 0),
    trans_fat_g     DOUBLE CHECK (trans_fat_g   IS NULL OR trans_fat_g   >= 0),
    sodium_mg       DOUBLE CHECK (sodium_mg     IS NULL OR sodium_mg     >= 0),
    cholesterol_mg  DOUBLE CHECK (cholesterol_mg IS NULL OR cholesterol_mg >= 0),

    label_version INT NOT NULL DEFAULT 1,     -- 같은 product의 라벨 버전 관리

    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                  ON UPDATE CURRENT_TIMESTAMP(6),

    CONSTRAINT fk_nutrition_product
        FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,

    CONSTRAINT uq_nutrition_product_label
        UNIQUE (product_id, label_version)
)
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE TABLE ingredient (
    id CHAR(36) PRIMARY KEY,                       -- 상품의 성분 설명에 대한 id (UUID)
    product_id CHAR(36) NOT NULL,

    raw_ingredient TEXT NOT NULL,                  -- 라벨 표기 원문, gpt가 이거 보고 진단 내림
    norm_text TEXT,                                -- 정규화를 하기 위한 문자열
    allergen_tags TEXT,                            -- JSON ["peanut","wheat"]
    order_index INTEGER NOT NULL DEFAULT 0,        -- 라벨마다의 순서가 있음

    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                  ON UPDATE CURRENT_TIMESTAMP(6),

    FOREIGN KEY(product_id) REFERENCES product(id) ON DELETE CASCADE
)
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE TABLE scan_history (
    id CHAR(36) PRIMARY KEY,                  -- 스캔 기록 UUID
    user_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,

    scanned_at DATETIME(6) NOT NULL,          -- 스캔 시각

    decision ENUM('avoid','caution','ok'),    -- NULL 허용(아직 분석 전 등)

    summary VARCHAR(255),                     -- 예: "당류 25g/회 → 고당"
    ai_total_score TINYINT UNSIGNED,          -- 0~100 (0~33 나쁨, 34~66 보통, 67~100 좋음)

    conditions JSON,                          -- ["diabetes", ...]
    allergies  JSON,                          -- ["peanut", ...]
    habits     JSON,                          -- ["low_sugar", ...]

    ai_allergy_report   TEXT,                 -- 예: "땅콩 알레르기 주의"
    ai_condition_report TEXT,                 -- 예: "당뇨 환자 주의"
    ai_alter_report     TEXT,                 -- 예: "저당 제품 추천"
    ai_vegan_report     TEXT,                 -- 예: "비건 제품 아님"
    ai_total_report     TEXT,                 -- 예: "당류 25g/회로 당뇨 환자 주의"

    caution_factors JSON,                     -- 예: [{"key":"heart_disease","level":"red"}, ...]

    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    deleted_at DATETIME(6) NULL,              -- soft delete

    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
)
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE TABLE user_daily_score (
  user_id         CHAR(36) NOT NULL COMMENT 'FK user(id)',         -- UUID
  local_date      DATE NOT NULL COMMENT '사용자 로컬 기준 날짜',    -- YYYY-MM-DD

  score           TINYINT UNSIGNED NOT NULL
                  CHECK (score BETWEEN 0 AND 100),

  -- 부가 지표
  num_scans       INT UNSIGNED NOT NULL DEFAULT 0,
  max_severity    ENUM('none','info','warning','danger') NULL,
  decision_counts JSON NULL,                                       -- {"ok":n,"caution":n,"avoid":n}

  -- 산식/버전/상태
  formula_version INT UNSIGNED NOT NULL DEFAULT 1,
  dirty           TINYINT(1) NOT NULL DEFAULT 0,                   -- 1이면 재계산 필요
  last_computed_at DATETIME(6) NULL,                               -- UTC

  -- 공통 메타
  created_at      DATETIME(6) NOT NULL
                  DEFAULT CURRENT_TIMESTAMP(6),
  updated_at      DATETIME(6) NOT NULL
                  DEFAULT CURRENT_TIMESTAMP(6)
                  ON UPDATE CURRENT_TIMESTAMP(6),
  deleted_at      DATETIME(6) NULL,                                -- soft delete (원하면 제거 가능)
  sync_state      TINYINT NOT NULL DEFAULT 1,                      -- 필요 없으면 서버에선 빼도 됨

  PRIMARY KEY (user_id, local_date),

  CONSTRAINT fk_user_daily_score_user
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
)
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_unicode_ci;