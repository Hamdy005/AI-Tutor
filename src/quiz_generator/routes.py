from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from src.quiz_generator.quiz import smart_quiz_generator
from src.store import get_material, get_chunks, get_summary, save_quiz
from src.dependencies import get_current_user_id, get_current_user
from src.config import settings

router = APIRouter(prefix="/api/quiz", tags=["Quiz"])


class QuizRequest(BaseModel):
    difficulty: str = "Medium"
    mcq_count: int = 4
    tf_count: int = 3
    source_type: str = "web"
    material_id: Optional[str] = None
    topic: Optional[str] = None


class QuizResponse(BaseModel):
    quiz: dict
    quiz_id: str


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    body: QuizRequest,
    user_id: str = Depends(get_current_user_id),
    current_user=Depends(get_current_user),
):
    if body.mcq_count < 1 or body.mcq_count > 20:
        raise HTTPException(400, "MCQ count must be between 1 and 20")
    if body.tf_count < 1 or body.tf_count > 20:
        raise HTTPException(400, "True/False count must be between 1 and 20")

    try:
        quiz = None
        material_id = body.material_id if body.source_type in ("pdf", "url") else None

        if body.source_type == "web":
            if not body.topic:
                raise HTTPException(400, "Topic is required for web-based quiz")
            quiz = smart_quiz_generator(
                difficulty=body.difficulty,
                mcq_count=body.mcq_count,
                tf_count=body.tf_count,
                topic_title=body.topic,
            )

        elif body.source_type in ("pdf", "url"):
            mat = get_material(body.material_id) if body.material_id else None
            if not mat:
                raise HTTPException(400, f"No {body.source_type} material found")

            chunks_list = get_chunks(body.material_id)
            chunks_texts = [c["content"] for c in chunks_list] if chunks_list else []
            summary_record = get_summary(body.material_id)
            summary_text = summary_record["summary"] if summary_record else None

            quiz = smart_quiz_generator(
                difficulty=body.difficulty,
                mcq_count=body.mcq_count,
                tf_count=body.tf_count,
                material_id=body.material_id if mat.get("status") == "ready" else None,
                summary=summary_text,
                chunks=chunks_texts,
            )
        else:
            raise HTTPException(400, f"Unknown source_type: {body.source_type}")

        saved = save_quiz(
            user_id=user_id,
            material_id=material_id,
            source_type=body.source_type,
            difficulty=body.difficulty,
            mcq_count=body.mcq_count,
            tf_count=body.tf_count,
            quiz_data=quiz,
            model_name=settings.model_name,
        )

        return QuizResponse(quiz=quiz, quiz_id=saved["id"])
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Quiz generation failed: {e}")
