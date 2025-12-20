import pandas as pd
import uuid
import json
import re
from app.core.database import SessionLocal
from app.models.product import Product
from app.models.nutrition import Nutrition
from app.models.ingredient import Ingredient

def clean_numeric(value):
    """'10g', '100mg', '1,200' 등의 문자열에서 숫자만 추출하여 float로 변환"""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    
    # 숫자와 소수점만 남기고 나머지 제거 (g, mg, 콤마 등)
    cleaned = re.sub(r'[^0-9.]', '', str(value))
    return float(cleaned) if cleaned else 0.0

def run_final_migration():
    try:
        df = pd.read_csv("제품정보.xlsx - Sheet1.csv", encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv("제품정보.xlsx - Sheet1.csv", encoding='cp949')

    df = df.where(pd.notnull(df), None)
    db = SessionLocal()

    try:
        for _, row in df.iterrows():
            product_id = str(uuid.uuid4())

            # 1. 알레르기 태그 처리
            raw_allergy_text = row['알레르기성분']
            allergy_list = [item.strip() for item in str(raw_allergy_text).split(',')] if raw_allergy_text else []

            # 2. Product 생성
            new_product = Product(
                id=product_id,
                name=row['제품명'],
                category=row['식품유형'],
                allergens=raw_allergy_text,
                trace_allergens=row['혼입가능성분'],
                barcode=row['바코드번호']
            )
            db.add(new_product)

            # 3. Ingredient 생성
            if row['원재료명']:
                new_ing = Ingredient(
                    id=str(uuid.uuid4()),
                    product_id=product_id,
                    raw_ingredient=row['원재료명'],
                    allergen_tags=json.dumps(allergy_list, ensure_ascii=False),
                    order_index=0
                )
                db.add(new_ing)

            # 4. Nutrition 생성 (단위 제거 및 컬럼명 매칭)
            # 엑셀 컬럼명에 따라 row['단백질(g)'] 또는 row['단백질']로 수정이 필요할 수 있습니다.
            new_nutrition = Nutrition(
                product_id=product_id,
                per_serving_grams=clean_numeric(row.get('1회 제공량', 0)),
                calories=clean_numeric(row.get('열량', 0)),
                sodium_mg=clean_numeric(row.get('나트륨(mg)', row.get('나트륨', 0))),
                carbs_g=clean_numeric(row.get('탄수화물(g)', row.get('탄수화물', 0))),
                sugar_g=clean_numeric(row.get('당류(g)', row.get('당류', 0))),
                fat_g=clean_numeric(row.get('지방(g)', row.get('지방', 0))),
                trans_fat_g=clean_numeric(row.get('트랜스지방(g)', row.get('트랜스지방', 0))),
                sat_fat_g=clean_numeric(row.get('포화지방(g)', row.get('포화지방', 0))),
                cholesterol_mg=clean_numeric(row.get('콜레스테롤(mg)', row.get('콜레스테롤', 0))),
                protein_g=clean_numeric(row.get('단백질(g)', row.get('단백질', 0))),
                label_version=1
            )
            db.add(new_nutrition)

        db.commit()
        print(f"✅ 데이터 삽입 완료!")

    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_final_migration()