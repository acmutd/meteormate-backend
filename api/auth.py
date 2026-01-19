# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import random
from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from firebase_admin import auth

from backend.database import get_db
from backend.models.user import User, UserRequestVerify, UserCompleteVerify, UserResetPassword
from backend.models.verification_codes import VerificationCodes, CodeType
from backend.utils.firebase_auth import get_current_user, get_firebase_user
from backend.utils.email import send_verification_email
from backend.schemas.user import UserCreate, UserResponse

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


async def get_firebase_and_uid(email: str = None, uid: str = None):
    try:
        if uid:
            firebase_user = await get_firebase_user(uid)
        elif email:
            firebase_user = auth.get_user_by_email(email)
        else:
            raise ValueError("Either email or uid must be provided")
        return firebase_user, firebase_user.uid
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=f"Error fetching user")


def create_verification_code(db: Session, uid: str, purpose: str) -> str:
    code = str(random.randint(100000, 999999))
    code_type = CodeType.PWD_RESET_CODE if purpose == "reset" else CodeType.ACC_VERIFICATION_CODE

    new_code = VerificationCodes(user_id=uid, code=code, type=code_type)
    try:
        db.add(new_code)
        db.commit()
        logger.info(f"User {uid} created a verification code for purpose {purpose}")
        return code

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB Error creating code for User {uid}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error creating verification code"
        )


def verify_code(db: Session, uid: str, code: str, purpose: str, consume: bool = False):
    """
    General helper func. for verifying 6-digit codes.
    :param db: Database connection
    :param uid: UID of the user in the request
    :param code: 6-digit code provided by the user
    :param purpose: Either `reset` for password reset or `verify` for email verification
    :param consume: Whether to delete the code from the DB after the check (defaults to False)
    """
    code_type = CodeType.PWD_RESET_CODE if purpose == "reset" else CodeType.ACC_VERIFICATION_CODE

    code_obj = db.query(VerificationCodes) \
        .filter(VerificationCodes.user_id == uid, VerificationCodes.type == code_type) \
        .order_by(VerificationCodes.created_at.desc()) \
        .first()

    if not code_obj:
        logger.warning(
            f"User {uid} attempted to {purpose}, but has no verification codes in the DB"
        )
        raise HTTPException(status_code=400, detail="No verification code found")
    if code_obj.created_at < datetime.utcnow() - timedelta(minutes=10):
        logger.warning(f"User {uid} attempted to {purpose} with an expired verification code")
        raise HTTPException(status_code=400, detail="Verification code expired")
    if code_obj.code != code:
        logger.warning(f"User {uid} attempted to {purpose} with an incorrect verification code")
        raise HTTPException(status_code=400, detail="Invalid verification code")

    if consume:
        try:
            db.delete(code_obj)
            db.commit()
            logger.info(
                f"User {uid}'s verification code with purpose '{purpose}' was deleted from the DB"
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"DB Error consuming code for User {uid}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error processing code")


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.utd_id == user_data.utd_id).first() \
       or db.query(User).filter(User.email == user_data.email).first():
        logger.warning("A user tried to create an account, but the email/Net ID was already in use")
        raise HTTPException(status_code=400, detail="Account already exists")

    try:
        firebase_user = auth.create_user(
            email=user_data.email, password=user_data.password, email_verified=False
        )

        new_user = User(
            id=firebase_user.uid,
            email=user_data.email,
            utd_id=user_data.utd_id,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except auth.EmailAlreadyExistsError:
        logger.warning("A user tried to create an account, but the email/Net ID was already in use")
        raise HTTPException(status_code=400, detail="Account already exists")
    except Exception as e:
        db.rollback()
        if 'firebase_user' in locals():
            try:
                auth.delete_user(firebase_user.uid)
            except:  # noqa
                pass
        logger.error(f"A user tried to create an account, but an error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating user")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user_token=Depends(get_current_user), db: Session = Depends(get_db)
):
    try:
        uid = current_user_token.get("uid")

        user = db.query(User).filter(User.id == uid).first()

        if not user:
            logger.warning(f"/me was requested, but the provided user does not exist")
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"User {uid} requested /me")

        return user

    except SQLAlchemyError as e:
        logger.error(f"Database error fetching profile for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/send-verification-code")
async def send_verification_code(request: UserRequestVerify, db: Session = Depends(get_db)):
    firebase_user, uid = await get_firebase_and_uid(email=request.email, uid=request.uid)

    purpose = request.purpose

    if purpose == "verify" and firebase_user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    if purpose == "reset" and not firebase_user.email_verified:
        raise HTTPException(status_code=400, detail="Email not verified yet")

    logger.info(f"User {uid} requested a verification code email for purpose {purpose}")

    code = create_verification_code(db, uid, request.purpose)

    try:
        await send_verification_email(str(request.email), code)
        logger.info(f"Successfully sent User {uid} an email for purpose {purpose}")
        return {"message": "Verification code sent to email"}
    except Exception as e:
        logger.error(f"There was an error sending an email to User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send verification code")


# this is called immediately upon user trying to reset password but NO "new password" is asked for/received
@router.post("/verify-reset-code")
async def verify_reset_code(request: UserCompleteVerify, db: Session = Depends(get_db)):
    _, uid = await get_firebase_and_uid(email=request.email)
    verify_code(db, uid, request.code, purpose="reset")  # verify w/o deleting from DB
    logger.info(f"User {uid} successfully verified their password reset code")
    return {"message": "Code verified"}


# second portion of reset password flow, user has already verified code & is now sending us the new pwd to use
@router.post("/reset-password")
async def reset_password(request: UserResetPassword, db: Session = Depends(get_db)):
    _, uid = await get_firebase_and_uid(email=request.email)
    # code gets verified a second time, consuming it this time
    verify_code(db, uid, request.code, purpose="reset")  # don't delete the code after use

    try:
        auth.update_user(uid, password=request.new_password)
    except Exception as e:
        logger.error(f"There was an error updating User {uid}'s password: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating password")

    # we eat the code AFTER Firebase runs w/o a hitch to avoid invalidating the code
    # after an unsuccessful attempt
    verify_code(db, uid, request.code, purpose="reset", consume=True)

    logger.info(f"User {uid} successfully updated their password")
    return {"message": "Password updated successfully"}


@router.post("/verify-email")
async def verify_email(request: UserCompleteVerify, db: Session = Depends(get_db)):
    _, uid = await get_firebase_and_uid(email=request.email)
    verify_code(db, uid, request.code, purpose="verify")  # verify w/o deletion'

    try:
        auth.update_user(uid, email_verified=True)
    except Exception as e:
        logger.error(f"There was an error verifying User {uid}'s email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating user")

    # keep this doubled/consuming AFTER Firebase checks to avoid codes being expired by Firebase errors
    verify_code(db, uid, request.code, purpose="verify", consume=True)  # verify & consume

    logger.info(f"User {uid} successfully verified their email")
    return {"message": "Email verified successfully"}


@router.post("/activity-ping")
def activity_ping(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_user.updated_at = datetime.utcnow()
        current_user.inactivity_notification_stage = None
        db.commit()
        logger.info(f"User {current_user.id} updated last login")
        return {"status": "ok"}

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to update activity for User {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error during activity ping")
