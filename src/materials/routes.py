import time
import validators
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel

from src.materials.text_utils import text_from_pdf, chunk_text, scrap_website
from src.rag.rag import store_embeddings
from src.store import create_material, update_material_status, save_chunks
from src.dependencies import get_current_user_id, get_current_user

router = APIRouter(prefix="/api/materials", tags=["Materials"])

ALLOWED_TYPES = {"application/pdf"}
MAX_SIZE_MB = 10
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024


def _validate_pdf_upload(file: UploadFile) -> None:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Only PDFs allowed")
    size = getattr(file, "size", None)
    if size is None:
        try:
            file.file.seek(0, 2)
            size = file.file.tell()
            file.file.seek(0)
        except Exception:
            size = None
    if size is not None and size > MAX_SIZE_BYTES:
        raise HTTPException(400, "File too large")
    if size is None:
        raise HTTPException(400, "File too large")


class URLInput(BaseModel):
    url: str


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    current_user=Depends(get_current_user),
):
    _validate_pdf_upload(file)

    try:
        material_id = None
        material = create_material(
            user_id=user_id,
            source_type="pdf",
            title=file.filename,
        )
        material_id = material["id"]

        raw = text_from_pdf(file.file)
        chunks = chunk_text(raw)
        chunk_ids = save_chunks(material_id, chunks)

        update_material_status(material_id, "processing")
        store_embeddings(material_id, chunk_ids, chunks)
        update_material_status(material_id, "ready")

        return {
            "material_id": material_id,
            "title": file.filename,
            "chunks_count": len(chunks),
        }
    except Exception as e:
        if material_id:
            update_material_status(material_id, "failed", str(e))
        raise HTTPException(500, f"Failed to process PDF: {e}")


@router.post("/scrape-url")
async def scrape_url(
    input: URLInput,
    user_id: str = Depends(get_current_user_id),
    current_user=Depends(get_current_user),
):
    if not validators.url(input.url):
        raise HTTPException(400, "Invalid URL provided")

    try:
        material = create_material(
            user_id=user_id,
            source_type="url",
            title=input.url,
            url=input.url,
        )
        material_id = material["id"]

        raw = scrap_website(input.url)
        chunks = chunk_text(raw, chunk_size=600, chunk_overlap=100)
        chunk_ids = save_chunks(material_id, chunks)

        update_material_status(material_id, "processing")
        store_embeddings(material_id, chunk_ids, chunks)
        update_material_status(material_id, "ready")

        return {
            "material_id": material_id,
            "title": input.url,
            "chunks_count": len(chunks),
        }
    except Exception as e:
        if material_id:
            update_material_status(material_id, "failed", str(e))
        raise HTTPException(500, f"Failed to scrape URL: {e}")



