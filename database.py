# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import logging
import enum as py_enum

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from config import settings
from exceptions import Conflict, InternalServerError, NotFound

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

ORMBase = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def commit_or_raise(
    db: Session, route_logger: logging.Logger, resource: str = "", uid: str = "", action: str = ""
):
    try:
        db.commit()
        route_logger.info(f"successfully completed {action} for {resource} (User: {uid})")

    except IntegrityError as e:
        db.rollback()
        err = str(e.orig).lower()

        if "foreign key" in err:
            route_logger.exception(f"{action} failed: foreign key violation on {resource} (User: {uid})")
            raise NotFound(resource)

        route_logger.exception(f"{action} failed: integrity conflict on {resource} (User: {uid})")
        raise Conflict(f"{resource} conflicts with existing data")

    except SQLAlchemyError:
        db.rollback()
        route_logger.exception(f"{action} failed: unexpected DB error on {resource} (User: {uid})")
        raise InternalServerError(f"Internal server error while {action} {resource}")
