# Created by Ryan Polasky | 1/4/26
# ACM MeteorMate | All Rights Reserved

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import text, and_
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import Settings
from app.models.user import User, InactivityStage
from app.utils.email import send_inactive_notices

router = APIRouter()


# noinspection SqlResolve,PyTypeChecker
@router.post("/clean-db")
def clean_db(x_cron_secret: str = Header(None), db: Session = Depends(get_db)):
    if x_cron_secret != Settings.CRON_SECRET or not Settings.CRON_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized request")

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
        print(f"Deleted {len(deleted_codes)} verification codes: {deleted_codes}")

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
        print(f"Deleted {len(deleted_users)} inactive users: {deleted_users}")

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
        print(f"Marked {len(marked_inactive)} users as inactive: {marked_inactive}")

    return {
        "deleted_verification_codes": len(deleted_codes),
        "deleted_users": len(deleted_users),
        "marked_inactive": len(marked_inactive),
    }


@router.post("/check-inactive-users")
def check_inactive_users(x_cron_secret: str = Header(None), db: Session = Depends(get_db)):
    """
    Check for users that should be inactive/are inactive & send appropriate notices via email
    """
    if x_cron_secret != Settings.CRON_SECRET or not Settings.CRON_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized request")

    now = datetime.utcnow()

    # 1 month warning (30 days inactive, no notification sent yet)
    thirty_days_ago = now - timedelta(days=30)
    users_need_one_month = db.query(User).filter(
        and_(User.updated_at < thirty_days_ago, User.inactivity_notification_stage.is_(None))
    ).all()

    for user in users_need_one_month:
        send_inactive_notices(email=str(user.email), notice_num=1)
        user.inactivity_notification_stage = InactivityStage.ONE_MONTH
        user.last_inactivity_notification_sent_at = now

    db.commit()

    # 1 week warning (53 days inactive, only sent 1-month)
    fifty_three_days_ago = now - timedelta(days=53)
    users_need_one_week = db.query(User).filter(
        and_(
            User.updated_at < fifty_three_days_ago,
            User.inactivity_notification_stage == InactivityStage.ONE_MONTH
        )
    ).all()

    for user in users_need_one_week:
        send_inactive_notices(email=str(user.email), notice_num=2)
        user.inactivity_notification_stage = InactivityStage.ONE_WEEK
        user.last_inactivity_notification_sent_at = now

    db.commit()

    # Mark inactive (60 days, only sent 1-week)
    sixty_days_ago = now - timedelta(days=60)
    users_need_inactive = db.query(User).filter(
        and_(
            User.updated_at < sixty_days_ago,
            User.inactivity_notification_stage == InactivityStage.ONE_WEEK
        )
    ).all()

    for user in users_need_inactive:
        send_inactive_notices(email=str(user.email), notice_num=3)
        user.inactivity_notification_stage = InactivityStage.INACTIVE
        user.last_inactivity_notification_sent_at = now
        user.is_active = False

    db.commit()
