from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.analysis import router as analysis_router
from services.model_service import model_service


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carga los modelos una sola vez al iniciar la API.
    model_service.load_models()
    yield


app = FastAPI(
    title="SentinelAI API",
    description="API REST para analisis de sentimiento y deteccion de bots con XLM-RoBERTa.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "nombre": "SentinelAI",
        "version": "1.0.0",
        "estado": "API activa",
        "documentacion": "/docs",
    }

