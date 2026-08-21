import os

import pytest

# Must run before anything imports app.db, so tests never touch the real
# Postgres DATABASE_URL from backend/.env.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture(autouse=True)
def clean_predictions_table():
    from app.db import Base, engine
    from app.models.db_models import PredictionRecord

    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(PredictionRecord.__table__.delete())
    yield


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
