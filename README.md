# Decision OS

An AI-assisted decision engine. Tell it what you're deciding between,
teach it what matters to you, and it scores the options, explains its
reasoning, and gets better over time from your feedback.

## Structure

```
decision-os/
├── backend/     FastAPI service — API, scoring engine, LLM integration
├── frontend/    Streamlit app — profile, decisions, history, insights
├── data/        Sample/seed data
└── docs/        Architecture and design notes
```

See [`docs/architecture.md`](docs/architecture.md) for a system overview and
[`docs/decision_engine.md`](docs/decision_engine.md) for how scoring and
learning work.

## Quickstart

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # then fill in DATABASE_URL / API keys
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`, with interactive
docs at `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
pip install streamlit pandas requests
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

### 3. Both, via Docker Compose

```bash
docker-compose up --build
```

## Running tests

```bash
cd backend
pytest
```

## Tech stack

- **Backend:** FastAPI, SQLAlchemy, Pydantic, Alembic
- **Frontend:** Streamlit
- **AI:** OpenAI / Google Gemini / Groq (pluggable provider layer)
- **Database:** PostgreSQL
