# Created by Atharva Mishra | 1/29/2026
# MeteorMate | All Rights Reserved

import uvicorn

from config import settings
from app import app

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG,
    )
