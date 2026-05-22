import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import import_models
from app.routes import auth, audit, clubs, dashboard, players, teams, upload, users

import_models()

os.makedirs("uploads/players", exist_ok=True)

app = FastAPI(
    title="API Liga de Fútbol del Huila",
    version="1.0.0",
    description="Sistema Web de Gestión de Liga de Fútbol del Huila",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clubs.router)
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(audit.router)
app.include_router(dashboard.router)
app.include_router(upload.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok", "service": "liga-futbol-huila-backend"}
