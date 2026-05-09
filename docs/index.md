# AI Tutor API — Documentation

Base URL: `http://localhost:8000`

Routes Overview:

- Materials: `docs/materials.md`
- Summarizer: `docs/summarizer.md`
- Tutor (RAG): `docs/rag.md`
- Quiz Generator: `docs/quiz_generator.md`

Quick Start:

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

All routes return JSON. Authentication is not yet implemented (planned: Supabase Google Auth).
