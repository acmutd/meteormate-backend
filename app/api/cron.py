# Created by Ryan Polasky | 1/4/26
# ACM MeteorMate | All Rights Reserved

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.config import Settings

router = APIRouter()


# noinspection SqlResolve,PyTypeChecker
@router.post("/clean-db")
async def clean_db(x_cron_secret: str = Header(None), db: AsyncSession = Depends(get_db)):
    if x_cron_secret != Settings.CRON_SECRET or not Settings.CRON_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized request")

    async with db.begin():
        # Clear expired verification codes
        result = await db.execute(
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
        result = await db.execute(
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
        result = await db.execute(
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
