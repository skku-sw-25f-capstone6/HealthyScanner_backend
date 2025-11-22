# app/services/image_storage_service.py
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
import mimetypes

class ImageStorageService:
    def __init__(self, base_dir: Path, base_url: str = "/static"):
        self.base_dir = base_dir
        self.base_url = base_url

    async def save_product_image(self, product_id: str, file: UploadFile) -> str:
        ext = mimetypes.guess_extension(file.content_type or "") or ".jpg"
        filename = f"product_{product_id}_{uuid4().hex}{ext}"

        dest_dir = self.base_dir / "products"
        dest_dir.mkdir(parents=True, exist_ok=True)

        full_path = dest_dir / filename
        content = await file.read()
        full_path.write_bytes(content)

        # DB에 저장할 URL (FastAPI에서 /static 으로 서빙한다고 가정)
        return f"{self.base_url}/products/{filename}"
