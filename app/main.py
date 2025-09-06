# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api import auth, survey, matches

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MeteorMate API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(survey.router, prefix="/api/survey", tags=["survey"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])


@app.get("/")
async def root():
    return {"message": "meteormate backend is in goblin mode"}


@app.get("/health")
async def health_check():
    return {"status": "goated"}
