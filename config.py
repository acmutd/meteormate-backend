# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import json
from decouple import config
from typing import List


class Settings:
    DATABASE_URL: str = config("DATABASE_URL")

    FIREBASE_CREDENTIALS = json.loads(
        config("FIREBASE_CREDENTIALS", default="{}")
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

    # admin user uid for testing
    ADMIN_UID: str = config("ADMIN_UID", default="")

    # validation config
    FIRST_NAME_MIN_LEN: int = 2
    FIRST_NAME_MAX_LEN: int = 50
    LAST_NAME_MIN_LEN: int = 2
    LAST_NAME_MAX_LEN: int = 50
    MIN_AGE: int = 16
    MAX_AGE: int = 80


settings = Settings()
