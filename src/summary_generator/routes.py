import time
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from src.summary_generator.summary import summarizer
from src.store import get_material, get_chunks, save_summary, get_summary as get_stored_summary
from src.dependencies import get_current_user_id, get_current_user
from src.config import settings

router = APIRouter(prefix="/api/materials", tags=["Summarizer"])


class SummarizeRequest(BaseModel):
    material_id: str


class SummarizeResponse(BaseModel):
    summary: str
    time_taken: float


@router.post("/summarize", response_model=SummarizeResponse)
async def generate_summary(
    body: SummarizeRequest,
    user_id: str = Depends(get_current_user_id),
    current_user=Depends(get_current_user),
):
    mat = get_material(body.material_id)
    if not mat:
        raise HTTPException(404, "Material not found")

    chunks_list = get_chunks(body.material_id)
    if not chunks_list:
        raise HTTPException(400, "No text chunks found in this material")

    try:
        combined = "\n".join(c["content"] for c in chunks_list)
        start = time.time()
        summary = summarizer(combined)
        elapsed = time.time() - start

        save_summary(
            material_id=body.material_id,
            user_id=user_id,
            summary=summary,
            time_taken=elapsed,
            model_name=settings.model_name,
        )

        return SummarizeResponse(summary=summary, time_taken=elapsed)
    except Exception as e:
        raise HTTPException(500, f"Summarization failed: {e}")


@router.get("/{material_id}/summary")
async def get_material_summary(
    material_id: str,
    user_id: str = Depends(get_current_user_id),
    current_user=Depends(get_current_user),
):
    summary = get_stored_summary(material_id)
    if not summary:
        raise HTTPException(404, "No summary found for this material")
    return {"summary": summary["summary"], "time_taken": summary.get("time_taken", 0)}
