# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.routes import auth, survey, matches, cron, profiles


def create_app() -> FastAPI:
    app = FastAPI(
        title="MeteorMate API",
        version="1.0.0",
    )

    # Logging
    logger = logging.getLogger("meteormate")
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handling
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
            request: Request, exc: RequestValidationError
    ):
        errors = []
        for error in exc.errors():
            field = error["loc"][-1] if error["loc"] else "unknown"

            if error["type"] == "missing":
                errors.append(f"{field} is required")
            elif error["type"] == "value_error":
                msg = error["msg"]
                if "Email must be a valid @utdallas.edu address" in msg:
                    errors.append("Email must be a valid @utdallas.edu address")
                else:
                    errors.append(f"{field}: {msg}")
            else:
                errors.append(f"{field}: {error['msg']}")

        return JSONResponse(
            status_code=422,
            content={"error": "Validation failed", "details": errors},
        )

    # Routes
    app.include_router(auth.router, prefix="/routes/auth", tags=["auth"])
    app.include_router(survey.router, prefix="/routes/survey", tags=["survey"])
    app.include_router(matches.router, prefix="/routes/matches", tags=["matches"])
    app.include_router(cron.router, prefix="/routes/cron", tags=["cron"])
    app.include_router(
        profiles.router, prefix="/routes/profiles", tags=["user_profiles"]
    )

    # Health / root
    @app.get("/")
    async def root():
        return {"message": "MeteorMate backend is online!"}

    @app.get("/health")
    async def health_check():
        return {"status": "Online"}

    return app


app = create_app()
