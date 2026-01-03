# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved
import uvicorn
import logging
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
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

def setup_logging(file_name: str = "app.log"):
    logger = logging.getLogger() # root logger
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # handler for printing logs to console/terminal
        console_handler = logging.StreamHandler(file_name)
        # handler for writing logs to file
        file_handler = logging.FileHandler()

        fmt = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(fmt)
        file_handler.setFormatter(fmt)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)


setup_logging()
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    # log the metadata associated with each request
    logger.info("{request.method} {request.url.path} - Completed with status {response.status_code}")
    logger.info(json.dumps(response.headers, indent=4)) # use JSON format instead of multi-line logs for readibility even on other logging platforms


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

    # NOTE: only logs validation errors, not other types of errors
    # use instead of logging.info() to avoid clashes with uvicorn's own internal logs
    logger.error(f"{request.method} {request.url.path} - Caught by valid_exception_handler (bad input). Errors: {errors}") 

    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "details": errors}
    )

# routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(survey.router, prefix="/api/survey", tags=["survey"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])


@app.get("/")
async def root():
    logger.info("Starting MeteorMate Backend!")
    return {"message": "MeteorMate backend is online!"}


@app.get("/health")
async def health_check():
    logger.info("Meteormate API is online!")
    return {"status": "Online"}

if __name__ == "__main__":
    logger.info("Starting Meteormate API")
    uvicorn.run(app, host="0.0.0.0", port=8000)
