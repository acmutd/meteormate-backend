# Created by Atharva Mishra | 1/30/2026
# ACM MeteorMate | All Rights Reserved

import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlalchemy.orm import Session

from database import commit_or_raise
from utils.exceptions import BadRequest
from models.verification_codes import CodeType, VerificationCodes


def create_verification_code(
    db: Session,
    route_logger: logging.Logger,
    uid: str,
    purpose: Literal["reset", "account"],
) -> str:
    '''
    Creates a verification code for a user for a specific purpose (password reset or account verification).
    If a code already exists for the user and purpose, it is deleted and replaced with a new code.
    
    Args:
        - db: SQLAlchemy Session object
        - route_logger: Logger object for logging
        - uid: User ID for whom the code is being created
        - purpose: The purpose of the code ("reset" for password reset, "account" for account verification)
    Returns:
        - code: The generated verification code as a string
    Raises:
        - BadRequest: If the purpose is invalid
        - InternalServerError: If there is an error creating the code in the database
    '''
    if purpose not in ["reset", "account"]:
        route_logger.error(
            f"Invalid purpose '{purpose}' for creating verification code for User {uid}"
        )
        raise BadRequest("Invalid purpose for verification code")

    code = str(random.randint(100000, 999999))
    code_type = (CodeType.PWD_RESET_CODE if purpose == "reset" else CodeType.ACC_VERIFICATION_CODE)

    existing_code = (
        db.query(VerificationCodes).filter(
            VerificationCodes.user_id == uid, VerificationCodes.type == code_type.value
        ).first()
    )

    if existing_code:
        db.delete(existing_code)

    new_code = VerificationCodes(user_id=uid, code=code, type=code_type)
    db.add(new_code)

    commit_or_raise(
        db,
        route_logger,
        resource=f"{purpose} verification code",
        uid=uid,
        action="create",
    )

    return code


def verify_code(
    db: Session,
    route_logger: logging.Logger,
    uid: str,
    code: str,
    purpose: Literal["reset", "account"],
):
    """
    Generator function for verifying a verification code for a user.
    Yields if the code is valid, and deletes the code from the database after use.

    Args:
        - db: SQLAlchemy Session object
        - route_logger: Logger object for logging
        - uid: User ID for whom the code is being verified
        - code: The verification code to verify
        - purpose: The purpose of the code ("reset" for password reset, "account" for account verification)
    
    Raises:
        - BadRequest: If the purpose is invalid, if no code is found, if the code is expired, or if the code is incorrect
        - InternalServerError: If there is an error deleting the code from the database after verification
    """
    if purpose not in ["reset", "account"]:
        route_logger.error(f"Invalid purpose '{purpose}' for verifying code for User {uid}")
        raise BadRequest("Invalid purpose for verification code")

    code_type = (
        CodeType.PWD_RESET_CODE.value
        if purpose == "reset" else CodeType.ACC_VERIFICATION_CODE.value
    )

    code_obj = (
        db.query(VerificationCodes).filter(
            VerificationCodes.user_id == uid, VerificationCodes.type == code_type
        ).order_by(VerificationCodes.created_at.desc()).first()
    )

    if not code_obj:
        route_logger.warning(
            f"User {uid} attempted to {purpose}, but has no verification codes in the DB"
        )
        raise BadRequest("No verification code found")

    expires_at = code_obj.created_at + timedelta(minutes=10)

    if datetime.now(timezone.utc) > expires_at:
        route_logger.warning(f"User {uid} attempted to {purpose} with an expired verification code")
        raise BadRequest("Verification code expired")
    if code_obj.code != code:
        route_logger.warning(
            f"User {uid} attempted to {purpose} with an incorrect verification code"
        )
        raise BadRequest("Invalid verification code")

    yield  # stop here

    db.delete(code_obj)

    commit_or_raise(
        db,
        route_logger,
        resource=f"{purpose} verification code",
        uid=uid,
        action="delete",
    )
