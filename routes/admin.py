import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import commit_or_raise, get_db
from models.admin import Banlist, Admins
from models.user import User
from utils.exceptions import Forbidden, NotFound, Conflict
from utils.firebase_auth import ensure_admin

logger = logging.getLogger("meteormate." + __name__)
router = APIRouter()


@router.post("/ban_user/{net_id}")
def ban_user(
    net_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(ensure_admin)],
):
    user = db.query(User).filter(User.utd_id == net_id).first()
    if not user:
        logger.warning(f"Attempted to ban non-existent user {net_id}")
        raise NotFound(f"User {net_id} not found")

    if db.query(Banlist).filter(Banlist.net_id == net_id).first():
        logger.warning(f"Attempted to ban already banned user {net_id}")
        raise Conflict(f"User {net_id} is already banned")

    banned_user = Banlist(net_id=net_id)
    user.is_banned = True

    db.add(banned_user)
    commit_or_raise(db, logger, resource="banlist entry", uid=net_id, action="create")

    db.refresh(user)
    db.refresh(banned_user)

    logger.info(f"User {net_id} (Net ID: {user.utd_id}) has been banned")
    return {"message": f"User {net_id} has been banned"}


@router.post("/unban_user/{net_id}")
def unban_user(
    net_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(ensure_admin)],
):
    ban_entry = db.query(Banlist).filter(Banlist.net_id == net_id).first()
    if not ban_entry:
        logger.warning(f"Attempted to unban non-banned user {net_id}")
        raise NotFound(f"User {net_id} is not currently banned")

    db.delete(ban_entry)

    user = db.query(User).filter(User.utd_id == net_id).first()
    if user:
        user.is_banned = False

    commit_or_raise(db, logger, resource="banlist entry", uid=net_id, action="delete")

    db.refresh(user) if user else None

    logger.info(f"User {net_id} has been unbanned")
    return {"message": f"User {net_id} has been unbanned"}


@router.post("/add_admin/{net_id}")
def add_admin(
    net_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(ensure_admin)],
):
    user = db.query(User).filter(User.utd_id == net_id).first()
    if not user:
        logger.warning(f"Attempted to add non-existent user {net_id} as admin")
        raise NotFound(f"User {net_id} not found")

    if db.query(Admins).filter(Admins.net_id == net_id).first():
        logger.warning(f"Attempted to add already-admin user {net_id} as admin again")
        raise Forbidden(f"User {net_id} is already an admin")

    new_admin = Admins(net_id=net_id)

    db.add(new_admin)
    commit_or_raise(db, logger, resource="admin entry", uid=net_id, action="create")

    logger.info(f"User {net_id} (Net ID: {user.utd_id}) has been added as an admin")
    return {"message": f"User {net_id} has been added as an admin"}


@router.post("/remove_admin/{net_id}")
def remove_admin(
    net_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(ensure_admin)],
):
    admin_entry = db.query(Admins).filter(Admins.net_id == net_id).first()
    if not admin_entry:
        logger.warning(f"Attempted to remove non-admin user {net_id} from admins")
        raise NotFound(f"User {net_id} is not an admin")

    db.delete(admin_entry)
    commit_or_raise(db, logger, resource="admin entry", uid=net_id, action="delete")

    logger.info(f"User {net_id} has been removed from admins")
    return {"message": f"User {net_id} has been removed from admins"}
