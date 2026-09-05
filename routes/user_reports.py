import logging
import uuid
from typing import Annotated
from urllib.parse import unquote, urlparse

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.user import User
from models.user_reports import UserReport
from schemas.user_reports import UserReportCreate
from utils.firebase_auth import ensure_email_verified
from utils.exceptions import BadRequest, Forbidden

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


def is_report_screenshot_url(url: str, reporter_uid: str) -> bool:
    parsed_url = urlparse(url)
    expected_path = f"/v0/b/{settings.FIREBASE_STORAGE_BUCKET}/o/user_reports/{reporter_uid}/"

    return (
        parsed_url.scheme == "https"
        and parsed_url.netloc == "firebasestorage.googleapis.com"
        and unquote(parsed_url.path).startswith(expected_path)
    )


@router.post("/report")
async def report_user(
    report_data: UserReportCreate,
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Session = Depends(get_db)
):
    if current_user.id == report_data.reportee_uid:
        raise Forbidden("You cannot report yourself")

    if len(report_data.screenshots) > 5:
        raise BadRequest("You can submit a maximum of 5 screenshots per report")

    description = report_data.description.strip()
    if not description:
        raise BadRequest("A report description is required")

    if any(
        not is_report_screenshot_url(screenshot_url, current_user.id)
        for screenshot_url in report_data.screenshots
    ):
        raise BadRequest("Screenshots must be uploaded to your report storage folder")

    new_report = UserReport(
        id=f"{current_user.id}_{report_data.reportee_uid}_{uuid.uuid4()}",
        reporter_uid=current_user.id,
        reportee_uid=report_data.reportee_uid,
        description=description,
        screenshots=report_data.screenshots
    )
    
    db.add(new_report)
    db.commit()
    
    logger.info(f"User {current_user.id} reported user {report_data.reportee_uid}")
    return {"message": "Report submitted successfully"}
