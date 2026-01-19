# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import logging
import enum as py_enum

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings

logger = logging.getLogger("meteormate." + __name__)


def to_db(v):
    if isinstance(v, py_enum.Enum):
        return v.value
    if isinstance(v, list):
        return [to_db(x) for x in v]
    return v


try:
    logger.info("Initializing database connection...")

    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

except Exception as e:
    logger.critical(f"Failed to initialize database engine: {str(e)}")
    raise

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
