import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.ollama_client import ollama_client
import uvicorn

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: check Ollama availability
    available = await ollama_client.is_available()
    if available:
        logger.info("Ollama is available at %s", settings.OLLAMA_BASE_URL)
    else:
        logger.warning("Ollama is not available at %s, will use rule-based fallback", settings.OLLAMA_BASE_URL)
    yield
    # Shutdown: close HTTP session
    await ollama_client.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8090"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to MindPulse - AI Enhanced Productivity Tool"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=settings.PORT
    )