# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from decouple import config
from typing import List


class Settings:
    DATABASE_URL: str = config("DATABASE_URL")
    FIREBASE_CREDENTIALS_PATH: str = config(
        "FIREBASE_CREDENTIALS_PATH", default="firebase-key.json"
    )
    ALLOWED_ORIGINS: List[str] = ["*"]  # todo - change this to meteormate.com when site is live
    DEBUG: bool = config("DEBUG", default=False, cast=bool)

    # ai service config
    GEMINI_API_KEY: str = config("GEMINI_API_KEY", default=None)
    GEMINI_MODEL: str = config("GEMINI_MODEL", default="gemini-2.5-flash-lite")

    # email config - might not need this at all
    SMTP_SERVER: str = config("SMTP_SERVER", default="")
    SMTP_PORT: int = config("SMTP_PORT", default=587, cast=int)
    EMAIL_USER: str = config("EMAIL_USER", default="")
    EMAIL_PASSWORD: str = config("EMAIL_PASSWORD", default="")

    # cron config (i.e. admin token for cron jobs to perform administrative duties)
    CRON_SECRET: str = config("CRON_SECRET", default="")

    # admin bearer key for testing
    ADMIN_BEARER: str = config("ADMIN_BEARER", default="")


settings = Settings()
