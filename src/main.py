from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.materials.routes import router as materials_router
from src.summary_generator.routes import router as summary_router
from src.rag.routes import router as tutor_router
from src.quiz_generator.routes import router as quiz_router

app = FastAPI(
    title="AI Tutor API",
    description="Backend API for the AI Tutor for Students application",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(materials_router)
app.include_router(summary_router)
app.include_router(tutor_router)
app.include_router(quiz_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "AI Tutor API"}
