# Created by Ryan Polasky | 7/12/25
# Updated by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError

from database import commit_or_raise, get_db
from config import settings
from utils.exceptions import BadRequest, Conflict, InternalServerError, NotFound
from models.user import User, UserRequestVerify, UserCompleteVerify, UserResetPassword
from utils.firebase_auth import get_current_user, get_firebase_and_uid
from utils.email import send_verification_email
from schemas.user import UserCreate, UserResponse
from utils.firebase_storage import delete_all_profile_pictures
from utils.verification_codes import create_verification_code, verify_code

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.utd_id == user_data.utd_id).first() \
        or db.query(User).filter(User.email == user_data.email).first():

        logger.warning("user tried to create an account with an existing email/Net ID in DB")
        raise Conflict("Account already exists")

    firebase_user = None

    try:
        firebase_user = auth.create_user(
            email=user_data.email, password=user_data.password, email_verified=False
        )

        new_user = User(id=firebase_user.uid, email=user_data.email, utd_id=user_data.utd_id)

        db.add(new_user)

        commit_or_raise(db, logger, resource="user", uid=new_user.id, action="create")

        db.refresh(new_user)
        return new_user

    except Exception:
        if firebase_user is not None:
            try:
                auth.delete_user(firebase_user.uid)
                logger.info(f"rolled back Firebase user {firebase_user.uid} after DB failure")
            except Exception:
                logger.exception("failed to rollback Firebase user", exc_info=settings.DEBUG)

        raise  # re-raise the original exception


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user_token=Depends(get_current_user), db: Session = Depends(get_db)
):
    uid = current_user_token.get("uid")

    user = db.query(User).filter(User.id == uid).first()

    if not user:
        logger.warning(f"User {uid} not found in DB during /me request")
        raise NotFound("User")

    logger.info(f"User {uid} requested /me")

    return user


@router.delete("/delete")
async def delete_user_account(
    current_user_token=Depends(get_current_user), db: Session = Depends(get_db)
):
    uid = current_user_token.get("uid")

    user = db.query(User).filter(User.id == uid).first()
    if not user:
        logger.warning(f"User {uid} not found in DB during account deletion")
        raise NotFound("User")

    user.pending_deletion = True
    commit_or_raise(db, logger, resource="user", uid=uid, action="mark for deletion")

    try:
        auth.delete_user(uid)
    except (ValueError, FirebaseError) as e:
        logger.error(f"Error deleting User {uid} account: {str(e)}", exc_info=settings.DEBUG)

        user.pending_deletion = False
        commit_or_raise(db, logger, resource="user", uid=uid, action="unmark for deletion")

        raise InternalServerError("Error deleting account")

    # important part idk how i forgot it first time
    delete_all_profile_pictures(uid)

    db.delete(user)

    try:
        commit_or_raise(db, logger, resource="user", uid=uid, action="delete")
    except Exception as e:
        logger.critical(
            f"Failed to delete User {uid} from DB after Firebase deletion (delete during cron): {str(e)}",
            exc_info=settings.DEBUG,
        )

    logger.info(f"User {uid} successfully deleted their account")

    return {"message": "Account deleted successfully"}


@router.post("/send-verification-code")
async def send_verification_code(request: UserRequestVerify, db: Session = Depends(get_db)):
    firebase_user, uid = await get_firebase_and_uid(email=request.email, uid=request.uid)

    purpose = request.purpose

    if purpose == "verify" and firebase_user.email_verified:
        raise BadRequest("Email already verified")
    if purpose == "reset" and not firebase_user.email_verified:
        raise BadRequest("Email not verified yet")

    logger.info(f"User {uid} requested a verification code for purpose {purpose}")

    code = create_verification_code(db, logger, uid, request.purpose)

    try:
        send_verification_email(str(request.email), code)
        logger.info(f"Successfully sent User {uid} an email for purpose {purpose}")
        return {"message": "Verification code sent to email"}

    except Exception as e:
        db.rollback()
        logger.error(
            f"There was an error sending an email to User {uid}: {str(e)}", exc_info=settings.DEBUG
        )

        raise InternalServerError("Failed to send verification code")


# this is called immediately upon user trying to reset password but NO "new password" is asked for/received
@router.post("/verify-reset-code")
async def verify_reset_code(request: UserCompleteVerify, db: Session = Depends(get_db)):
    _, uid = await get_firebase_and_uid(email=request.email)

    verify_code(db, logger, uid, request.code, purpose="reset")  # verify w/o deleting from DB

    logger.info(f"User {uid} successfully verified their password reset code")

    return {"message": "Code verified"}


# second portion of reset password flow, user has already verified code & is now sending us the new pwd to use
@router.post("/reset-password")
async def reset_password(request: UserResetPassword, db: Session = Depends(get_db)):
    _, uid = await get_firebase_and_uid(email=request.email)
    # code gets verified a second time, consuming it this time
    verify_code(db, logger, uid, request.code, purpose="reset")  # don't delete the code after use

    try:
        auth.update_user(uid, password=request.new_password)
    except Exception as e:
        logger.error(
            f"There was an error updating User {uid}'s password: {str(e)}", exc_info=settings.DEBUG
        )
        raise InternalServerError("Error updating password")

    # we eat the code AFTER Firebase runs w/o a hitch to avoid invalidating the code
    # after an unsuccessful attempt
    verify_code(db, logger, uid, request.code, purpose="reset", consume=True)

    logger.info(f"User {uid} successfully updated their password")
    return {"message": "Password updated successfully"}


@router.post("/verify-email")
async def verify_email(request: UserCompleteVerify, db: Session = Depends(get_db)):
    _, uid = await get_firebase_and_uid(email=request.email)
    verify_code(db, logger, uid, request.code, purpose="verify")  # verify w/o deletion'

    try:
        auth.update_user(uid, email_verified=True)
    except Exception as e:
        logger.error(
            f"There was an error verifying User {uid}'s email: {str(e)}", exc_info=settings.DEBUG
        )
        raise InternalServerError("Error updating user")

    # keep this doubled/consuming AFTER Firebase checks to avoid codes being expired by Firebase errors
    verify_code(db, logger, uid, request.code, purpose="verify", consume=True)  # verify & consume

    logger.info(f"User {uid} successfully verified their email")
    return {"message": "Email verified successfully"}


@router.get("/activity-ping")
def activity_ping(current_user_token=Depends(get_current_user), db: Session = Depends(get_db)):
    uid = current_user_token.get("uid")

    current_user = db.query(User).filter(User.id == uid).first()
    if not current_user:
        logger.warning(f"User {uid} not found in DB during activity ping")
        raise NotFound("User")

    current_user.updated_at = datetime.now(timezone.utc)
    current_user.inactivity_notification_stage = None

    commit_or_raise(db, logger, resource="user", uid=current_user.id, action="update")

    return {"status": "ok"}
