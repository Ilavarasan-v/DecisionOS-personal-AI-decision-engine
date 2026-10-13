from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import api_router
from backend.app.database.connection import Base, engine

# Import models so SQLAlchemy knows about all tables
# before create_all() runs.
from backend.app.models import (
    Decision,
    DecisionOption,
    DecisionScore,
    Feedback,
    Preference,
    PreferenceHistory,
    User,
)

# Create database tables.
Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="DecisionOS",
    description="Personal AI Decision Engine",
    version="0.1.0",
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
# Allow the React/Vite development server to communicate
# with the FastAPI backend.
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/")
def root():
    return {
        "message": "DecisionOS API is running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }