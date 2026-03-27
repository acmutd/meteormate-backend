# Created by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError

from database import get_db
from config import settings
from schemas.user import UserResetPassword, UserVerifyEmail
from utils.exceptions import (
    BadRequest,
    Forbidden,
    InternalServerError,
)
from models.user import User
from utils.firebase_auth import get_current_user, get_firebase_user
from utils.email import send_verification_email

from utils.verification_codes import create_verification_code, verify_code

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.get("/account_verification")
def send_account_verification_email(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    uid = current_user.id
    email = current_user.email
    firebase_user = get_firebase_user(uid=uid)

    if firebase_user.email_verified:
        logger.info(f"User {uid} requested email verification but email is already verified")
        raise BadRequest("Email is already verified")

    logger.info(f"User {uid} requested a verification code for email verification")

    code = create_verification_code(db, logger, uid, "account")

    try:
        send_verification_email(str(email), code)
        logger.info(f"Successfully sent User {uid} an email for account verification")
        return {"message": "Verification code sent to email"}

    except Exception as e:
        db.rollback()
        logger.error(
            f"There was an error sending an email to User {uid}: {str(e)}",
            exc_info=settings.DEBUG,
        )

        raise InternalServerError("Failed to send verification code")


@router.post("/account_verification")
def account_verification(
    code_data: UserVerifyEmail,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    uid = current_user.id

    verify_gen = verify_code(db, logger, uid, code_data.code, purpose="account")
    next(verify_gen)  # raises if code is invalid, expired, or missing

    try:
        auth.update_user(uid, email_verified=True)
        next(verify_gen, None)  # consume code after Firebase update succeeds, raises if error happens during deletion
    except Exception as e:
        logger.error(
            f"There was an error verifying User {uid}'s email: {str(e)}",
            exc_info=settings.DEBUG,
        )
        raise InternalServerError("Error updating user")

    logger.info(f"User {uid} successfully verified their account")
    return {"message": "Email verified successfully"}


@router.get("/reset_password/{email}")
def send_reset_password_email(
    email: str,
    db: Annotated[Session, Depends(get_db)],
):
    user = get_firebase_user(email=email)
    if not user.email_verified:
        logger.warning(f"Password reset requested for email {email} but email is not verified")
        raise Forbidden("Email is not verified")

    uid = user.uid
    logger.info(f"User {uid} requested a verification code for reset password")

    code = create_verification_code(db, logger, uid, "reset")

    try:
        send_verification_email(str(email), code)
        logger.info(f"Successfully sent User {uid} an email for reset password")
        return {"message": "Verification code sent to email"}

    except Exception as e:
        db.rollback()
        logger.error(
            f"There was an error sending an email to User {uid}: {str(e)}",
            exc_info=settings.DEBUG,
        )

        raise InternalServerError("Failed to send verification code")


@router.post("/reset_password")
def reset_password(
    request: UserResetPassword,
    db: Annotated[Session, Depends(get_db)],
):
    user = get_firebase_user(email=request.email)
    if not user.email_verified:
        logger.warning(
            f"Password reset attempted for email {request.email} but email is not verified"
        )
        raise Forbidden("Email is not verified")

    uid = user.uid
    verify_gen = verify_code(db, logger, uid, request.code, purpose="reset")
    next(verify_gen)

    # lil troll hehe
    if request.new_password:
        raise BadRequest("Password cannot be the same as old password")

    try:
        auth.update_user(uid, password=request.new_password)
        next(verify_gen, None)  # consume code after Firebase update succeeds
    except FirebaseError as e:
        logger.error(
            f"There was an error resetting password for User {uid}: {str(e)}",
            exc_info=settings.DEBUG,
        )
        raise InternalServerError("Error updating user")

    logger.info(f"User {uid} successfully reset their password")
    return {"message": "Password reset successfully"}
