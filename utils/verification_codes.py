import logging
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import commit_or_raise
from exceptions import BadRequest
from models.verification_codes import CodeType, VerificationCodes


def create_verification_code(
    db: Session, route_logger: logging.Logger, uid: str, purpose: str
) -> str:
    code = str(random.randint(100000, 999999))
    code_type = CodeType.PWD_RESET_CODE if purpose == "reset" else CodeType.ACC_VERIFICATION_CODE

    new_code = VerificationCodes(user_id=uid, code=code, type=code_type)
    db.add(new_code)

    commit_or_raise(
        db, route_logger, resource=f"{purpose} verification code", uid=uid, action="create"
    )

    return code


def verify_code(
    db: Session,
    route_logger: logging.Logger,
    uid: str,
    code: str,
    purpose: str,
    consume: bool = False
):
    """
    General helper func. for verifying 6-digit codes.
    :param db: Database connection
    :param uid: UID of the user in the request
    :param code: 6-digit code provided by the user
    :param purpose: Either `reset` for password reset or `verify` for email verification
    :param consume: Whether to delete the code from the DB after the check (defaults to False)
    """
    code_type = CodeType.PWD_RESET_CODE.value if purpose == "reset" else CodeType.ACC_VERIFICATION_CODE.value

    code_obj = db.query(VerificationCodes).filter(
        VerificationCodes.user_id == uid, VerificationCodes.type == code_type
    ).order_by(VerificationCodes.created_at.desc()).first()

    expires_at = code_obj.created_at + timedelta(minutes=10)

    if not code_obj:
        route_logger.warning(
            f"User {uid} attempted to {purpose}, but has no verification codes in the DB"
        )
        raise BadRequest("No verification code found")
    if datetime.now(timezone.utc) > expires_at:
        route_logger.warning(f"User {uid} attempted to {purpose} with an expired verification code")
        raise BadRequest("Verification code expired")
    if code_obj.code != code:
        route_logger.warning(
            f"User {uid} attempted to {purpose} with an incorrect verification code"
        )
        raise BadRequest("Invalid verification code")

    if consume:
        db.delete(code_obj)

        commit_or_raise(
            db, route_logger, resource=f"{purpose} verification code", uid=uid, action="delete"
        )
