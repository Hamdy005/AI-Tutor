import time
import asyncio
import logging
import validators
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, Header
from pydantic import BaseModel
from postgrest.exceptions import APIError

from src.materials.text_utils import text_from_pdf, chunk_text, scrap_website
from src.rag.rag import store_embeddings, store_embeddings_async
from src.store import create_material, get_material, update_material_status, save_chunks, list_materials, delete_material, rename_material, is_title_taken
from src.dependencies import get_current_user_id, get_current_user
from src.database import get_supabase, get_auth_supabase

logger = logging.getLogger(__name__)

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

@router.get("")
async def get_materials(
    user_id: str = Depends(get_current_user_id),
    current_user=Depends(get_current_user),
):
    return list_materials(user_id)

@router.get("/{material_id}")
async def get_material_by_id(
    material_id: str,
    user_id: str = Depends(get_current_user_id),
    current_user=Depends(get_current_user),
):
    mat = get_material(material_id)
    if not mat:
        raise HTTPException(404, "Material not found")
    return mat

async def _process_pdf_background(material_id: str, file_content: bytes):
    try:
        # Skip processing if this user already has a material with this title
        mat = get_material(material_id)
        if mat and is_title_taken(mat.get("title", ""), exclude_id=material_id, user_id=mat.get("user_id")):
            logger.info(f"Skipping processing for {material_id}: duplicate title")
            update_material_status(material_id, "failed", "Duplicate title. Please rename to retry.")
            return

        loop = asyncio.get_event_loop()
        from io import BytesIO
        raw = await loop.run_in_executor(None, text_from_pdf, BytesIO(file_content))
        chunks = await loop.run_in_executor(None, chunk_text, raw)
        chunk_ids = await loop.run_in_executor(None, save_chunks, material_id, chunks)

        update_material_status(material_id, "processing")
        await store_embeddings_async(material_id, chunk_ids, chunks)
        update_material_status(material_id, "ready")
        logger.info(f"Background processing complete for material {material_id}")
    except Exception as e:
        logger.error(f"Background processing failed for material {material_id}: {e}", exc_info=True)
        update_material_status(material_id, "failed", str(e))

async def _process_url_background(material_id: str, url: str):
    try:
        # Skip if this user already has a material with this title
        mat = get_material(material_id)
        if mat and is_title_taken(mat.get("title", ""), exclude_id=material_id, user_id=mat.get("user_id")):
            logger.info(f"Skipping URL processing for {material_id}: duplicate title, waiting for rename")
            return

        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(None, scrap_website, url)
        chunks = await loop.run_in_executor(None, lambda: chunk_text(raw, chunk_size=600, chunk_overlap=100))
        chunk_ids = await loop.run_in_executor(None, save_chunks, material_id, chunks)

        update_material_status(material_id, "processing")
        await store_embeddings_async(material_id, chunk_ids, chunks)
        update_material_status(material_id, "ready")
        logger.info(f"Background processing complete for URL material {material_id}")
    except Exception as e:
        logger.error(f"Background processing failed for URL material {material_id}: {e}", exc_info=True)
        update_material_status(material_id, "failed", str(e))

@router.post("/upload-pdf")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    current_user=Depends(get_current_user),
):
    _validate_pdf_upload(file)

    try:
        content = await file.read()
        material = create_material(
            user_id=user_id,
            source_type="pdf",
            title=file.filename,
        )
        material_id = material["id"]

        background_tasks.add_task(_process_pdf_background, material_id, content)

        return {
            "status": "processing_started",
            "material_id": material_id,
            "title": file.filename,
        }
    except Exception as e:
        logger.error(f"upload_pdf failed: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to start PDF processing: {e}")

@router.post("/scrape-url")
async def scrape_url(
    input: URLInput,
    background_tasks: BackgroundTasks,
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

        # Skip processing if title conflicts — user must rename first
        if not is_title_taken(input.url, exclude_id=material_id, user_id=user_id):
            background_tasks.add_task(_process_url_background, material_id, input.url)

        return {
            "status": "processing_started",
            "material_id": material_id,
            "title": input.url,
        }
    except Exception as e:
        logger.error(f"scrape_url failed: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to start scraping: {e}")

class RenameMaterialRequest(BaseModel):
    title: str

class BulkDeleteRequest(BaseModel):
    material_ids: list[str]

@router.post("/bulk-delete")
async def bulk_delete_materials(
    body: BulkDeleteRequest,
    user_id: str = Depends(get_current_user_id),
    current_user=Depends(get_current_user),
):
    from concurrent.futures import ThreadPoolExecutor

    def _delete_one(mid: str):
        mat = get_material(mid)
        if mat and mat.get("user_id") == user_id:
            delete_material(mid)

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=min(len(body.material_ids), 8)) as pool:
        await asyncio.gather(
            *[loop.run_in_executor(pool, _delete_one, mid) for mid in body.material_ids]
        )
    return {"status": "ok"}

@router.patch("/{material_id}")
async def rename_material_endpoint(
    material_id: str,
    body: RenameMaterialRequest,
    user_id: str = Depends(get_current_user_id),
    current_user=Depends(get_current_user),
):
    loop = asyncio.get_event_loop()
    mat = await loop.run_in_executor(None, lambda: get_material(material_id))
    if not mat:
        raise HTTPException(404, "Material not found")
    if mat.get("user_id") != user_id:
        raise HTTPException(403, "Not authorized to rename this material")
    new_title = body.title.strip()
    if not new_title:
        raise HTTPException(400, "Title cannot be empty")
    existing = await loop.run_in_executor(None, lambda: list_materials(user_id))
    if any(m.get("id") != material_id and m.get("title", "").strip().lower() == new_title.lower() for m in existing):
        raise HTTPException(409, "A material with this title already exists")
    await loop.run_in_executor(None, lambda: rename_material(material_id, new_title))

    # If the material was pending due to title conflict, try processing now
    if mat.get("source_type") == "url" and mat.get("status") == "pending":
        url = mat.get("url")
        if url and not is_title_taken(new_title, exclude_id=material_id, user_id=user_id):
            asyncio.ensure_future(_process_url_background(material_id, url))

    return {"status": "ok"}

class TopicRequest(BaseModel):
    topic: str

@router.post("/topic")
async def create_topic(
    body: TopicRequest,
    user_id: str = Depends(get_current_user_id)
):
    if is_title_taken(body.topic, user_id=user_id):
        raise HTTPException(409, "A material with this title already exists")
    mat = create_material(
        user_id=user_id,
        title=body.topic.strip(),
        source_type="topic"
    )
    update_material_status(mat["id"], "ready", "Topic ready")
    return {"material_id": mat["id"], "title": mat["title"]}


class SearchRequest(BaseModel):
    q: str

@router.post("/search")
async def search_materials(
    body: SearchRequest,
    user_id: str = Depends(get_current_user_id)
):
    supabase = get_supabase()
    if not supabase:
         return {"results": []}
         
    result = supabase.rpc(
        "search_materials_by_title",
        {"p_query": body.q, "p_user_id": user_id}
    ).execute()

    return {"results": result.data}
    
@router.delete("/{material_id}")
async def delete_material_endpoint(
    material_id: str,
    user_id: str = Depends(get_current_user_id),
    current_user=Depends(get_current_user),
):
    mat = get_material(material_id)
    if not mat:
        raise HTTPException(404, "Material not found")
    if mat.get("user_id") != user_id:
        raise HTTPException(403, "Not authorized to delete this material")
    delete_material(material_id)
    return {"status": "ok"}
