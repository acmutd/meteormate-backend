import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import commit_or_raise, get_db
from models.admin import Banlist, Admins
from models.user import User
from utils.exceptions import Forbidden, NotFound
from utils.firebase_auth import ensure_admin

logger = logging.getLogger("meteormate." + __name__)
router = APIRouter()


@router.post("/ban_user/{user_id}")
def ban_user(
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(ensure_admin)],
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Attempted to ban non-existent user {user_id}")
        raise NotFound(f"User {user_id} not found")

    banned_user = Banlist(user_id=user_id, net_id=user.net_id)

    db.add(banned_user)
    commit_or_raise(db, logger, resource="banlist entry", uid=user_id, action="create")

    logger.info(f"User {user_id} (Net ID: {user.net_id}) has been banned")
    return {"message": f"User {user_id} has been banned"}


@router.post("/unban_user/{user_id}")
def unban_user(
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(ensure_admin)],
):
    ban_entry = db.query(Banlist).filter(Banlist.user_id == user_id).first()
    if not ban_entry:
        logger.warning(f"Attempted to unban non-banned user {user_id}")
        raise NotFound(f"User {user_id} is not currently banned")

    db.delete(ban_entry)
    commit_or_raise(db, logger, resource="banlist entry", uid=user_id, action="delete")

    logger.info(f"User {user_id} has been unbanned")
    return {"message": f"User {user_id} has been unbanned"}


@router.post("/add_admin/{user_id}")
def add_admin(
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(ensure_admin)],
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Attempted to add non-existent user {user_id} as admin")
        raise NotFound(f"User {user_id} not found")

    existing_admin = db.query(Admins).filter(Admins.user_id == user_id).first()
    if existing_admin:
        logger.warning(f"Attempted to add already-admin user {user_id} as admin again")
        raise Forbidden(f"User {user_id} is already an admin")

    new_admin = Admins(user_id=user_id, net_id=user.net_id)

    db.add(new_admin)
    commit_or_raise(db, logger, resource="admin entry", uid=user_id, action="create")

    logger.info(f"User {user_id} (Net ID: {user.net_id}) has been added as an admin")
    return {"message": f"User {user_id} has been added as an admin"}


@router.post("/remove_admin/{user_id}")
def remove_admin(
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(ensure_admin)],
):
    admin_entry = db.query(Admins).filter(Admins.user_id == user_id).first()
    if not admin_entry:
        logger.warning(f"Attempted to remove non-admin user {user_id} from admins")
        raise NotFound(f"User {user_id} is not an admin")

    db.delete(admin_entry)
    commit_or_raise(db, logger, resource="admin entry", uid=user_id, action="delete")

    logger.info(f"User {user_id} has been removed from admins")
    return {"message": f"User {user_id} has been removed from admins"}
