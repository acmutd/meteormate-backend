# Created by Atharva Mishra | 9/16/2026
# ACM MeteorMate | All Rights Reserved

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import commit_or_raise, get_db
from models.notifications import Notifications
from models.user import User
from schemas.notifications import NotificationsGetResponse, NotificationsMarkSeenBody
from utils.exceptions import InternalServerError
from utils.firebase_auth import ensure_email_verified

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.get("/user_notifications", response_model=NotificationsGetResponse)
async def get_user_notifications(
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        notifications = (
            db.query(Notifications)
            .filter(
                Notifications.user_id == current_user.id, Notifications.seen == False
            )
            .all()
        )
        logger.info(f"User {current_user.id} fetched notifications")
        return {"data": notifications}
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching notifications for user {current_user.id}: {e!s}"
        )
        raise InternalServerError("Database error fetching notifications")
    except Exception:
        logger.exception(
            f"Unexpected error fetching notifications for user {current_user.id}"
        )
        raise InternalServerError("Unexpected error fetching notifications")


@router.post("/mark_notifications_seen")
async def mark_notifications_seen(
    notification_ids: NotificationsMarkSeenBody,
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        notifications = (
            db.query(Notifications)
            .filter(
                Notifications.user_id == current_user.id, Notifications.seen == False
            )
            .all()
        )
        for notification in notifications:
            if notification.id in notification_ids.notification_ids:
                notification.seen = True

        commit_or_raise(db)
        logger.info(f"User {current_user.id} marked notifications as seen")
        return {
            "message": f"Notifications marked {len(notification_ids.notification_ids)} as seen"
        }
    except SQLAlchemyError as e:
        logger.error(
            f"Database error marking notifications as seen for user {current_user.id}: {e!s}"
        )
        raise InternalServerError("Database error marking notifications as seen")
    except Exception:
        logger.exception(
            f"Unexpected error marking notifications as seen for user {current_user.id}"
        )
        raise InternalServerError("Unexpected error marking notifications as seen")
