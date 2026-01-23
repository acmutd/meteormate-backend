# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import logging
import sys

import firebase_admin
import uvicorn
from firebase_admin import credentials
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base
from app.api import auth, survey, matches, cron, profiles

logger = logging.getLogger("meteormate")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

logger.propagate = False

# noinspection PyProtectedMember
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {"storageBucket": "meteormate.firebasestorage.app"})
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.critical(f"Failed to initialize Firebase Admin SDK: {str(e)}")
        raise

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "unknown"

        if error["type"] == "missing":
            errors.append(f"{field} is required")
        elif error["type"] == "value_error":
            # extract custom validation message
            msg = error["msg"]
            if "Email must be a valid @utdallas.edu address" in msg:
                errors.append("Email must be a valid @utdallas.edu address")
            else:
                errors.append(f"{field}: {msg}")
        else:
            errors.append(f"{field}: {error['msg']}")

    return JSONResponse(status_code=422, content={"error": "Validation failed", "details": errors})


# routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(survey.router, prefix="/api/survey", tags=["survey"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(cron.router, prefix="/api/cron", tags=["cron"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["user_profiles"])


@app.get("/")
async def root():
    return {"message": "MeteorMate backend is online!"}


@app.get("/health")
async def health_check():
    return {"status": "Online"}


if __name__ == "__main__":
    logging.info("Successfully started backup!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
