# Customer Churn Predictor

A full-stack application that predicts customer churn using a machine learning model, served through a REST API and visualized in an interactive React dashboard.

![CI](https://github.com/YOUR_USERNAME/churn-predictor/actions/workflows/ci.yml/badge.svg)

## Live Demo

- **Frontend**: [churn-predictor-lilac.vercel.app](https://churn-predictor-lilac.vercel.app)
- **Backend API docs**: [churn-predictor-api-n7lu.onrender.com/docs](https://churn-predictor-api-n7lu.onrender.com/docs)

> **Note**: the backend runs on Render's free tier, which spins down after periods of inactivity. If the app has been idle, the first request may take 30–50 seconds to respond while the server wakes back up — subsequent requests are fast.

## Overview

This project demonstrates an end-to-end data science + software engineering workflow:

1. **Data & Model** — a scikit-learn classification model trained on a public customer churn dataset (e.g. [Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)).
2. **Backend API** — a FastAPI service that loads the trained model and exposes prediction endpoints.
3. **Frontend Dashboard** — a React + TypeScript app that lets users input customer data and visualize churn risk and key drivers.
4. **Infrastructure** — Dockerized services, PostgreSQL for storing prediction history, and a GitHub Actions CI pipeline running tests on every push.

## Tech Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| ML / Data  | Python, pandas, scikit-learn, SHAP   |
| Backend    | FastAPI, SQLAlchemy, PostgreSQL (psycopg3) |
| Frontend   | React, TypeScript, Vite, Recharts    |
| Testing    | pytest, Vitest                       |
| DevOps     | Docker, Docker Compose, GitHub Actions |

## Project Structure

```
churn-predictor/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── models/       # Pydantic schemas + DB models
│   │   ├── services/     # ML model loading & prediction logic
│   │   └── tests/        # pytest test suite
│   ├── data/              # Dataset + trained model artifacts
│   ├── train_model.py     # Script to train and export the model
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # App pages/views
│   │   └── services/      # API client
│   └── package.json
├── .github/workflows/ci.yml
├── docker-compose.yml
└── CLAUDE.md               # Project context for Claude Code
```

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python train_model.py       # trains and saves the model
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:5173`.

### Docker (both services)

```bash
docker compose up --build
```

## Deployment

- **Frontend** is deployed on [Vercel](https://vercel.com), built from `frontend/` with `VITE_API_URL` pointing at the Render backend.
- **Backend** is deployed on [Render](https://render.com) as a Docker web service, with `DATABASE_URL` pointing at a Render-managed PostgreSQL instance and `ALLOWED_ORIGINS` set to the Vercel frontend's URL for CORS.

## Roadmap

- [ ] Train baseline model and expose `/predict` endpoint
- [ ] Build dashboard with prediction form and result visualization
- [x] Add prediction history stored in PostgreSQL
- [x] Add model explainability (SHAP values) to the API
- [x] Deploy backend (Render/Fly.io) and frontend (Vercel)

## License

MIT
