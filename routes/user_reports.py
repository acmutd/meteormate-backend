import logging
import uuid
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
        raise BadRequest("At least one screenshot is required to submit a report")
    
    if len(report_data.screenshots) > 5:
        raise BadRequest("You can submit a maximum of 5 screenshots per report")

    new_report = UserReport(
        id=f"{current_user.id}_{report_data.reportee_uid}_{uuid.uuid4()}",
        reporter_uid=current_user.id,
        reported_uid=report_data.reportee_uid,
        description=report_data.description,
        screenshots=report_data.screenshots
    )
    
    db.add(new_report)
    db.commit()
    
    logger.info(f"User {current_user.id} reported user {report_data.reportee_uid}")
    return {"message": "Report submitted successfully"}
