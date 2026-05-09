from typing import Optional
from langchain.memory import ConversationBufferMemory
from src.database import get_supabase


def _db():
    client = get_supabase()
    if client is None:
        raise RuntimeError(
            "Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY in config.env."
        )
    return client


# ── Materials ──────────────────────────────────────────

def create_material(user_id: str, source_type: str, title: str,
                    file_path: Optional[str] = None,
                    url: Optional[str] = None) -> dict:
    data = {
        "user_id": user_id,
        "source_type": source_type,
        "title": title,
        "status": "pending",
    }
    if file_path:
        data["file_path"] = file_path
    if url:
        data["url"] = url
    result = _db().table("materials").insert(data).execute()
    return result.data[0]


def update_material_status(material_id: str, status: str,
                           error_message: Optional[str] = None):
    data = {"status": status}
    if error_message:
        data["error_message"] = error_message
    _db().table("materials").update(data).eq("id", material_id).execute()


def get_material(material_id: str) -> Optional[dict]:
    result = _db().table("materials").select("*").eq("id", material_id).execute()
    return result.data[0] if result.data else None


# ── Material Chunks ────────────────────────────────────

def save_chunks(material_id: str, chunks: list[str]) -> list[str]:
    records = [
        {"material_id": material_id, "chunk_index": i, "content": c}
        for i, c in enumerate(chunks)
    ]
    result = _db().table("material_chunks").insert(records).execute()
    return [r["id"] for r in result.data]


def get_chunks(material_id: str) -> list[dict]:
    result = (
        _db().table("material_chunks")
        .select("*")
        .eq("material_id", material_id)
        .order("chunk_index")
        .execute()
    )
    return result.data


# ── Summaries ──────────────────────────────────────────

def save_summary(material_id: str, user_id: str, summary: str,
                 time_taken: float, model_name: str = ""):
    data = {
        "material_id": material_id,
        "user_id": user_id,
        "summary": summary,
        "status": "completed",
        "time_taken": time_taken,
        "model_name": model_name,
    }
    _db().table("summaries").upsert(data, on_conflict=["material_id"]).execute()


def get_summary(material_id: str) -> Optional[dict]:
    result = (
        _db().table("summaries")
        .select("*")
        .eq("material_id", material_id)
        .maybe_single()
        .execute()
    )
    return result.data if result.data else None


# ── Quizzes ────────────────────────────────────────────

def save_quiz(user_id: str, material_id: Optional[str], source_type: str,
              difficulty: str, mcq_count: int, tf_count: int,
              quiz_data: dict, model_name: str = "") -> dict:
    data = {
        "user_id": user_id,
        "source_type": source_type,
        "difficulty": difficulty,
        "mcq_count": mcq_count,
        "tf_count": tf_count,
        "quiz_data": quiz_data,
        "status": "completed",
        "model_name": model_name,
    }
    if material_id:
        data["material_id"] = material_id
    result = _db().table("quizzes").insert(data).execute()
    return result.data[0]


# ── Conversation Memory (in-memory, ephemeral) ─────────

import uuid as _uuid

_memories: dict[str, ConversationBufferMemory] = {}


def get_or_create_memory(memory_id: Optional[str] = None):
    if memory_id and memory_id in _memories:
        return _memories[memory_id], memory_id
    mid = memory_id or str(_uuid.uuid4())
    mem = ConversationBufferMemory(
        input_key="input", memory_key="chat_history", return_messages=True
    )
    _memories[mid] = mem
    return mem, mid
