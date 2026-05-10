import time
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from src.rag.rag import rag_answer
from src.dependencies import get_current_user
from src.store import get_material, get_chunks, get_summary, get_or_create_memory

router = APIRouter(prefix="/api/tutor", tags=["Tutor"])


class TutorQuery(BaseModel):
    query: str
    source_type: str = "web"
    material_id: Optional[str] = None
    memory_id: Optional[str] = None


class TutorResponse(BaseModel):
    answer: str
    source: str
    time_taken: float
    memory_id: str


@router.post("/ask", response_model=TutorResponse)
async def ask_tutor(
    body: TutorQuery,
    current_user=Depends(get_current_user),
):
    if not body.query.strip():
        raise HTTPException(400, "Query cannot be empty")

    memory, memory_id = get_or_create_memory(body.memory_id)
    start = time.time()

    try:
        if body.source_type in ("pdf", "url"):
            mat = get_material(body.material_id) if body.material_id else None
            if not mat:
                raise HTTPException(400, f"No {body.source_type} material found. Upload one first.")

            material_id = body.material_id
            chunks_list = get_chunks(material_id)
            chunks_texts = [c["content"] for c in chunks_list] if chunks_list else []
            summary_record = get_summary(material_id)
            summary_text = summary_record["summary"] if summary_record else ""
            status = mat.get("status")

            if status == "ready":
                answer, memory = rag_answer(
                    query=body.query, material_id=material_id, memory=memory
                )
                source = f"{body.source_type.upper()} (embeddings)"
            elif summary_text:
                answer, memory = rag_answer(
                    query=body.query, summaries=summary_text, memory=memory
                )
                source = f"{body.source_type.upper()} (summary)"
            elif chunks_texts:
                answer, memory = rag_answer(
                    query=body.query, chunks=chunks_texts, memory=memory
                )
                source = f"{body.source_type.upper()} (chunks)"
            else:
                answer, memory = rag_answer(query=body.query, memory=memory)
                source = "Web Search (no material data)"

        else:
            answer, memory = rag_answer(query=body.query, memory=memory)
            source = "Web Search"

    except Exception as e:
        raise HTTPException(500, f"Error generating answer: {e}")

    elapsed = time.time() - start
    return TutorResponse(answer=answer, source=source, time_taken=elapsed, memory_id=memory_id)
