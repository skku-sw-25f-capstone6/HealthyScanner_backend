import pandas as pd
import uuid
import json
import re
import traceback
from app.core.database import SessionLocal
from app.models.product import Product
from app.models.nutrition import Nutrition
from app.models.ingredient import Ingredient

def clean_numeric(value):
    if value is None or pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r'[^0-9.]', '', str(value))
    return float(cleaned) if cleaned else 0.0

def run_final_migration():
    try:
        df = pd.read_excel("product_data.csv", engine='openpyxl')
        print("✅ 엑셀 파일을 정상적으로 로드했습니다.")
    except Exception as e:
        print(f"❌ 파일 읽기 실패: {e}")
        return

    df.columns = [col.strip() for col in df.columns]
    df = df.where(pd.notnull(df), None)

    db = SessionLocal()
    try:
        for idx, (row_idx, row) in enumerate(df.iterrows()):
            product_id = str(uuid.uuid4())

            # 1. 알레르기 태그
            raw_allergy = row.get('알레르기성분')
            allergy_list = [item.strip() for item in str(raw_allergy).split(',')] if raw_allergy else []

            # 2. Product 생성
            new_product = Product(
                id=product_id,
                name=row.get('제품명'),
                category=row.get('식품유형'),
                allergens=raw_allergy,
                trace_allergens=row.get('혼입가능성분'),
                barcode=str(row.get('바코드번호', ''))
            )
            db.add(new_product)
            db.flush() # 부모 ID 등록

            # 3. Ingredient 생성
            if row.get('원재료명'):
                new_ing = Ingredient(
                    id=str(uuid.uuid4()),
                    product_id=product_id,
                    raw_ingredient=row.get('원재료명'),
                    allergen_tags=json.dumps(allergy_list, ensure_ascii=False),
                    order_index=0
                )
                db.add(new_ing)

            # 4. Nutrition 생성 (수정된 부분: id 추가)
            new_nutrition = Nutrition(
                id=str(uuid.uuid4()),  # 🔥 여기가 핵심입니다! ID를 직접 생성해줘야 합니다.
                product_id=product_id,
                per_serving_grams=clean_numeric(row.get('1회 제공량', 0)),
                calories=clean_numeric(row.get('열량(kcal)', 0)),
                sodium_mg=clean_numeric(row.get('나트륨(mg)', 0)),
                carbs_g=clean_numeric(row.get('탄수화물(g)', 0)),
                sugar_g=clean_numeric(row.get('당류(g)', 0)),
                fat_g=clean_numeric(row.get('지방(g)', 0)),
                trans_fat_g=clean_numeric(row.get('트랜스지방(g)', 0)),
                sat_fat_g=clean_numeric(row.get('포화지방(g)', 0)),
                cholesterol_mg=clean_numeric(row.get('콜레스테롤(mg)', 0)),
                protein_g=clean_numeric(row.get('단백질(g)', 0)),
                label_version=1
            )
            db.add(new_nutrition)

            if idx % 10 == 0:
                print(f"🚀 {idx}번째 처리 중: {row.get('제품명')}")

        db.commit()
        print(f"✅ 총 {len(df)}개의 데이터 마이그레이션 성공!")

    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_final_migration()