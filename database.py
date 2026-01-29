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
    '''
    Commits the current transaction to the database session and handles exceptions.
    Args:
        db (Session): The SQLAlchemy database session.
        route_logger (logging.Logger): Logger for logging route-specific messages.
        resource (str): The resource being acted upon usually the db table name.
        uid (str): The user ID associated with the action.
        action (str): The action being performed *in present tense*. 
    Raises:
        NotFound: If a foreign key constraint is violated.
        Conflict: If there is an integrity conflict with existing data.
        InternalServerError: For any other unexpected database errors.
    '''
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
