from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Eager load the multilingual model on the main thread during startup
    # This completely prevents Apple Silicon MPS framework thread-deadlocks 
    # that occur if initialized for the first time inside a BackgroundTask
    try:
        from app.services.embeddings.multilingual_model import multilingual_model
        multilingual_model.get_model()
    except Exception as e:
        print(f"Startup warning: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Documentation Q&A Chatbot",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "provider": settings.LLM_PROVIDER}

# Routers will be included here later
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
