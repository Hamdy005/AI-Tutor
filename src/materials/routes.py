import time
import validators
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel

from src.materials.text_utils import text_from_pdf, chunk_text, scrap_website
from src.rag.rag import store_embeddings
from src.store import create_material, update_material_status, save_chunks
from src.dependencies import get_current_user_id

router = APIRouter(prefix="/api/materials", tags=["Materials"])


class URLInput(BaseModel):
    url: str


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
):
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    try:
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
