from typing import Optional
from datetime import datetime, timezone
from langchain.memory import ConversationBufferMemory
from src.database import get_supabase

_in_memory: dict = {
    "materials": {},
    "material_chunks": {},
    "summaries": {},
    "quizzes": {},
    "users": {},
    "next_id": 0,
}


def _get_next_id() -> str:
    _in_memory["next_id"] += 1
    return str(_in_memory["next_id"])


def _db():
    client = get_supabase()
    if client is not None:
        return client
    return None


def _table_supabase(table: str):
    client = _db()
    if client is not None:
        return client.table(table)

    class _FakeTable:
        def __init__(self, name):
            self.name = name

        def insert(self, data):
            if isinstance(data, list):
                for item in data:
                    item["id"] = item.get("id", _get_next_id())
                    _in_memory.setdefault(self.name, {})[item["id"]] = item
                class R:
                    data = data
                return R()
            data["id"] = data.get("id", _get_next_id())
            _in_memory.setdefault(self.name, {})[data["id"]] = data
            class R:
                data = [data]
            return R()

        def select(self, *args):
            return self

        def eq(self, field, value):
            self._eq_field = field
            self._eq_value = value
            return self

        def order(self, field):
            return self

        def maybe_single(self):
            records = list(_in_memory.get(self.name, {}).values())
            if hasattr(self, '_eq_field'):
                records = [r for r in records if r.get(self._eq_field) == self._eq_value]
            return self._make_response(records[0] if records else None)

        def execute(self):
            records = list(_in_memory.get(self.name, {}).values())
            if hasattr(self, '_eq_field'):
                records = [r for r in records if r.get(self._eq_field) == self._eq_value]
            if hasattr(self, '_order_field'):
                records.sort(key=lambda r: r.get(self._order_field, 0))
            return self._make_response(records)

        def update(self, data):
            self._update_data = data
            return self

        def _make_response(self, data):
            class R:
                pass
            r = R()
            r.data = data if isinstance(data, list) else ([data] if data else [])
            return r

    return _FakeTable(table)


# ── Materials ──────────────────────────────────────────

def list_materials(user_id: str) -> list[dict]:
    sup = _table_supabase("materials")
    if sup is not None and not isinstance(sup.execute().__class__.__name__, '_FakeTable'):
        try:
            result = sup.select("*").eq("user_id", user_id).order("created_at").execute()
            return list(reversed(result.data))
        except Exception:
            pass
    records = list(_in_memory.get("materials", {}).values())
    return list(reversed([r for r in records if r.get("user_id") == user_id]))


def create_material(user_id: str, source_type: str, title: str,
                    file_path: Optional[str] = None,
                    url: Optional[str] = None,
                    topic: Optional[str] = None) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    data = {"user_id": user_id, "source_type": source_type, "title": title, "status": "pending",
            "created_at": now, "updated_at": now}
    if file_path:
        data["file_path"] = file_path
    if url:
        data["url"] = url
    if topic:
        data["topic"] = topic
    result = _table_supabase("materials").insert(data).execute()
    return result.data[0]


def update_material_status(material_id: str, status: str,
                           error_message: Optional[str] = None):
    data = {"status": status}
    if error_message:
        data["error_message"] = error_message
    _table_supabase("materials").update(data).eq("id", material_id).execute()


def get_material(material_id: str) -> Optional[dict]:
    result = _table_supabase("materials").select("*").eq("id", material_id).execute()
    return result.data[0] if result.data else None


# ── Material Chunks ────────────────────────────────────

def save_chunks(material_id: str, chunks: list[str]) -> list[str]:
    records = [
        {"material_id": material_id, "chunk_index": i, "content": c}
        for i, c in enumerate(chunks)
    ]
    result = _table_supabase("material_chunks").insert(records).execute()
    return [r["id"] for r in result.data]


def get_chunks(material_id: str) -> list[dict]:
    result = (
        _table_supabase("material_chunks")
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
    tbl = _table_supabase("summaries")
    existing = tbl.select("*").eq("material_id", material_id).execute()
    if existing.data:
        tbl.update(data).eq("material_id", material_id).execute()
    else:
        tbl.insert(data).execute()


def get_summary(material_id: str) -> Optional[dict]:
    result = (
        _table_supabase("summaries")
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
    result = _table_supabase("quizzes").insert(data).execute()
    return result.data[0]


def get_quizzes(material_id: Optional[str] = None, user_id: Optional[str] = None) -> list[dict]:
    tbl = _table_supabase("quizzes")
    result = tbl.select("*").execute()
    records = result.data
    if material_id:
        records = [r for r in records if r.get("material_id") == material_id]
    if user_id:
        records = [r for r in records if r.get("user_id") == user_id]
    return records


# ── Users ────────────────────────────────────────────

def create_user(name: str, email: str, password: str) -> dict:
    existing = get_user_by_email(email)
    if existing:
        raise ValueError("Email already registered")
    data = {"name": name, "email": email, "password": password}
    result = _table_supabase("users").insert(data).execute()
    return result.data[0]


def get_user_by_email(email: str) -> Optional[dict]:
    result = _table_supabase("users").select("*").eq("email", email).maybe_single().execute()
    return result.data[0] if result.data else None


def get_user_by_id(user_id: str) -> Optional[dict]:
    result = _table_supabase("users").select("*").eq("id", user_id).maybe_single().execute()
    return result.data[0] if result.data else None


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
