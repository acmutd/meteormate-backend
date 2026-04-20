import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.user_reports import UserReport
from schemas.user_reports import UserReportCreate
from utils.firebase_auth import ensure_email_verified
from utils.exceptions import BadRequest, Forbidden

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.post("/report")
async def report_user(
    report_data: UserReportCreate,
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Session = Depends(get_db)
):
    if current_user.id == report_data.reportee_uid:
        raise Forbidden("You cannot report yourself")

    if not report_data.screenshots:
        logger.warning(f"User {current_user.id} submitted a report without screenshots")
        
    
