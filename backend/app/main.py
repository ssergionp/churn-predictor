import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import predictions
from app.db import Base, engine
from app.models import db_models  # noqa: F401 - registers PredictionRecord with Base.metadata

DEFAULT_ALLOWED_ORIGINS = "http://localhost:5173"


def _get_allowed_origins() -> list[str]:
    """Reads ALLOWED_ORIGINS as a comma-separated list of origins, falling
    back to the local Vite dev server if it's not set.
    """
    raw = os.environ.get("ALLOWED_ORIGINS")
    if raw:
        source = "the ALLOWED_ORIGINS env var"
    else:
        source = f"the default (ALLOWED_ORIGINS is not set) - {DEFAULT_ALLOWED_ORIGINS!r}"
    origins = [origin.strip() for origin in (raw or DEFAULT_ALLOWED_ORIGINS).split(",") if origin.strip()]

    print(f"[cors] ALLOWED_ORIGINS loaded from: {source}")
    print(f"[cors] Effective allow_origins passed to CORSMiddleware: {origins}")

    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Customer Churn Predictor API",
    description="Serves churn predictions from a trained scikit-learn model.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predictions.router, prefix="/api", tags=["predictions"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
