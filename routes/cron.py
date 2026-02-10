# Created by Ryan Polasky | 1/4/26
# ACM MeteorMate | All Rights Reserved

from datetime import datetime, timedelta
import logging

from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import text, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from config import Settings, settings
from models.user import User, InactivityStage
from utils.email import send_inactive_notices
from utils.exceptions import InternalServerError, Unauthorized

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


# noinspection SqlResolve,PyTypeChecker
@router.post("/clean-db")
def clean_db(x_cron_secret: str = Header(None), db: Session = Depends(get_db)):
    if x_cron_secret != Settings.CRON_SECRET or not Settings.CRON_SECRET:
        logger.warning("Unauthorized attempt to access /clean-db")
        raise HTTPException(status_code=401, detail="Unauthorized request")

    logger.info("Starting scheduled DB cleanup task")

    try:
        with db.begin():
            # Clear expired verification codes
            result = db.execute(
                text(
                    """
                DELETE FROM verification_codes
                WHERE created_at < now() - interval '10 minutes'
                RETURNING id
            """
                )
            )
            deleted_codes = [row[0] for row in result.fetchall()]
            if deleted_codes:
                logger.info(f"Deleted {len(deleted_codes)} expired verification codes")

            # Delete inactive users not logged in for >=2 years
            result = db.execute(
                text(
                    """
                DELETE FROM public.users
                WHERE is_active = false
                AND updated_at < now() - interval '2 years'
                RETURNING id
            """
                )
            )
            deleted_users = [row[0] for row in result.fetchall()]
            if deleted_users:
                logger.info(
                    f"Deleted {len(deleted_users)} long-term inactive users: {deleted_users}"
                )

            # Mark dormant users as inactive (2+ months)
            result = db.execute(
                text(
                    """
                UPDATE public.users
                SET is_active = false
                WHERE is_active = true
                AND updated_at < now() - interval '2 months'
                RETURNING id
            """
                )
            )
            marked_inactive = [row[0] for row in result.fetchall()]
            if marked_inactive:
                logger.info(f"Marked {len(marked_inactive)} users as inactive due to dormancy")

        logger.info("DB cleanup task completed successfully")
        return {
            "deleted_verification_codes": len(deleted_codes),
            "deleted_users": len(deleted_users),
            "marked_inactive": len(marked_inactive),
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error during cleanup task: {str(e)}", stack_info=settings.DEBUG)
        raise HTTPException(status_code=500, detail="Database error during cleanup")
    except Exception as e:
        logger.error(f"Unexpected error during cleanup task: {str(e)}", stack_info=settings.DEBUG)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/check-inactive-users")
async def check_inactive_users(x_cron_secret: str = Header(None), db: Session = Depends(get_db)):
    """
    Check for users that should be inactive/are inactive & send appropriate notices via email.
    Runs in 3 steps so a failure in one doesn't stop the others.
    """
    if x_cron_secret != Settings.CRON_SECRET or not Settings.CRON_SECRET:
        logger.warning("Unauthorized attempt to access /check-inactive-users")
        raise HTTPException(status_code=401, detail="Unauthorized request")

    logger.info("Starting inactive user check...")
    now = datetime.utcnow()
    results = {"one_month": 0, "one_week": 0, "inactive": 0}

    # 1 month warning
    try:
        thirty_days_ago = now - timedelta(days=30)
        users_need_one_month = db.query(User).filter(
            and_(User.updated_at < thirty_days_ago, User.inactivity_notification_stage.is_(None))
        ).all()

        for user in users_need_one_month:
            try:
                await send_inactive_notices(email=str(user.email), notice_num=1)

                # only update DB if email succeeded
                user.inactivity_notification_stage = InactivityStage.ONE_MONTH
                user.last_inactivity_notification_sent_at = now
                results["one_month"] += 1
            except Exception as email_err:
                logger.error(
                    f"Failed to send 1-month notice to User {user.id}: {email_err}",
                    stack_info=settings.DEBUG
                )
                continue

        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB Error processing 1-month warnings: {str(e)}", stack_info=settings.DEBUG)

    # 1 week warning
    try:
        fifty_three_days_ago = now - timedelta(days=53)
        users_need_one_week = db.query(User).filter(
            and_(
                User.updated_at < fifty_three_days_ago,
                User.inactivity_notification_stage == InactivityStage.ONE_MONTH
            )
        ).all()

        for user in users_need_one_week:
            try:
                await send_inactive_notices(email=str(user.email), notice_num=2)

                user.inactivity_notification_stage = InactivityStage.ONE_WEEK
                user.last_inactivity_notification_sent_at = now
                results["one_week"] += 1
            except Exception as email_err:
                logger.error(
                    f"Failed to send 1-week notice to User {user.id}: {email_err}",
                    stack_info=settings.DEBUG
                )
                continue

        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB Error processing 1-week warnings: {str(e)}", stack_info=settings.DEBUG)

    # Mark inactive
    try:
        sixty_days_ago = now - timedelta(days=60)
        users_need_inactive = db.query(User).filter(
            and_(
                User.updated_at < sixty_days_ago,
                User.inactivity_notification_stage == InactivityStage.ONE_WEEK
            )
        ).all()

        for user in users_need_inactive:
            try:
                await send_inactive_notices(email=str(user.email), notice_num=3)

                user.inactivity_notification_stage = InactivityStage.INACTIVE
                user.last_inactivity_notification_sent_at = now
                user.is_active = False
                results["inactive"] += 1
            except Exception as email_err:
                logger.error(
                    f"Failed to send inactive notice to User {user.id}: {email_err}",
                    stack_info=settings.DEBUG
                )
                continue

        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB Error processing final inactivity: {str(e)}", stack_info=settings.DEBUG)

    logger.info(f"Inactive user check complete. Results: {results}")
    return results


@router.post("/delete_pending_users")
async def delete_pending_users(x_cron_secret: str = Header(None), db: Session = Depends(get_db)):
    if x_cron_secret != Settings.CRON_SECRET or not Settings.CRON_SECRET:
        logger.warning("Unauthorized attempt to access /delete_pending_users")
        raise Unauthorized("Unauthorized request")

    logger.info("Starting scheduled DB cleanup task for pending delete users")

    try:
        with db.begin():
            # delete user where pending_deletion is true
            deleted_users = db.query(User).where(User.pending_deletion.is_(True)
                                                 ).delete(synchronize_session=False)

            logger.info(f"Deleted {deleted_users} delete pending users from DB")

        logger.info("Delete pending user cleanup task completed successfully")
        return {"deleted_users": deleted_users}
    except SQLAlchemyError as e:
        logger.error(
            f"Database error during delete pending user cleanup task: {str(e)}",
            stack_info=settings.DEBUG
        )
        raise InternalServerError("Database error during cleanup")
