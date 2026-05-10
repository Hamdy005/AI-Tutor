from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.materials.routes import router as materials_router
from src.summary_generator.routes import router as summary_router
from src.rag.routes import router as tutor_router
from src.quiz_generator.routes import router as quiz_router
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.rag.rag import get_embedder
    get_embedder()
    yield


app = FastAPI(
    title="AI Tutor API",
    description="Backend API for the AI Tutor for Students application",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins or ["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(materials_router)
app.include_router(summary_router)
app.include_router(tutor_router)
app.include_router(quiz_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "AI Tutor API"}
