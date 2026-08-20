from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import predictions

app = FastAPI(
    title="Customer Churn Predictor API",
    description="Serves churn predictions from a trained scikit-learn model.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predictions.router, prefix="/api", tags=["predictions"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
