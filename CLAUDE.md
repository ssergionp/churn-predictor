# Project: Customer Churn Predictor

Full-stack app: Python ML model served via FastAPI, consumed by a React + TypeScript dashboard.

## Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL, scikit-learn, pandas
- **Frontend**: React 18, TypeScript, Vite, Recharts
- **Testing**: pytest (backend), Vitest (frontend)
- **Infra**: Docker, Docker Compose, GitHub Actions

## Project Structure

- `backend/app/api/` — FastAPI route handlers
- `backend/app/models/` — Pydantic schemas and SQLAlchemy DB models
- `backend/app/services/` — model loading, prediction, and business logic
- `backend/app/tests/` — pytest test suite
- `backend/train_model.py` — trains the churn model and saves it to `backend/data/model.pkl`
- `frontend/src/components/` — reusable UI components
- `frontend/src/pages/` — top-level views
- `frontend/src/services/` — API client (axios/fetch wrappers)

## Commands

```bash
# Backend
cd backend && source .venv/bin/activate && pytest -q
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

# Frontend
cd frontend && npm run test
cd frontend && npm run dev

# Full stack
docker compose up --build
```

## Conventions

- Write all code, comments, and commit messages in English (portfolio project for international employers).
- Backend: follow PEP 8, type hints everywhere, Pydantic for request/response validation.
- Frontend: functional components with hooks, TypeScript strict mode, no `any`.
- Every new feature should include at least one test.
- Keep commits small and descriptive (conventional commits style: `feat:`, `fix:`, `test:`, `docs:`).

## Current Status

Project scaffolding only. Next step: implement `train_model.py` and the `/predict` endpoint.
