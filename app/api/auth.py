# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from firebase_admin import auth

from app.database import get_db
from app.models.user import User, UserRequestVerify, UserCompleteVerify, UserResetPassword
from app.models.verification_codes import VerificationCodes, CODE_TYPE_ENUM
from app.utils.firebase_auth import get_current_user, get_firebase_user
from app.utils.email import send_verification_email
from app.schemas.user import UserCreate, UserResponse, UserSurveyResponse
from app.models.survey import Survey

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
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")


def create_verification_code(db: Session, uid: str, purpose: str) -> str:
    code = str(random.randint(100000, 999999))
    code_type = CODE_TYPE_ENUM.PWD_RESET_CODE if purpose == "reset" else CODE_TYPE_ENUM.ACC_VERIFICATION_CODE

    new_code = VerificationCodes(user_id=uid, code=code, type=code_type)
    db.add(new_code)
    db.commit()
    return code


def verify_code(db: Session, uid: str, code: str, purpose: str, consume: bool = False):
    """
    General helper func. for verifying 6 digit codes.
    :param db: Database connection
    :param uid: UID of the user in the request
    :param code: 6 digit code provided by the user
    :param purpose: Either `reset` for password reset or `verify` for email verification
    :param consume: Whether to delete the code from the DB after the check (defaults to False)
    """
    code_type = CODE_TYPE_ENUM.PWD_RESET_CODE if purpose == "reset" else CODE_TYPE_ENUM.ACC_VERIFICATION_CODE

    code_obj = db.query(VerificationCodes)\
                 .filter(VerificationCodes.user_id == uid, VerificationCodes.type == code_type)\
                 .order_by(VerificationCodes.created_at.desc())\
                 .first()

    if not code_obj:
        raise HTTPException(status_code=400, detail="No verification code found")
    if code_obj.created_at < datetime.utcnow() - timedelta(minutes=10):
        raise HTTPException(status_code=400, detail="Verification code expired")
    if code_obj.code != code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    if consume:
        db.delete(code_obj)
        db.commit()


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.utd_id == user_data.utd_id).first() \
       or db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Account already exists")

    try:
        firebase_user = auth.create_user(
            email=user_data.email, password=user_data.password, email_verified=False
        )
        new_user = User(
            id=firebase_user.uid,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            birthdate=user_data.birthdate,
            utd_id=user_data.utd_id,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Account already exists")
    except Exception as e:
        db.rollback()
        if 'firebase_user' in locals():
            try:
                auth.delete_user(firebase_user.uid)
            except:  # noqa
                pass
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.get("/me", response_model=UserSurveyResponse)
async def get_current_user_profile(
    current_user_token=Depends(get_current_user), db: Session = Depends(get_db)
):
    uid = current_user_token.get("uid")
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    survey = db.query(Survey).filter(Survey.user_id == uid).first()
    return {"user": user, "survey": survey or None}


@router.post("/send-verification-code")
async def send_verification_code(request: UserRequestVerify, db: Session = Depends(get_db)):
    firebase_user, uid = await get_firebase_and_uid(email=request.email, uid=request.uid)

    if request.purpose == "verify" and firebase_user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    if request.purpose == "reset" and not firebase_user.email_verified:
        raise HTTPException(status_code=400, detail="Email not verified yet")

    code = create_verification_code(db, uid, request.purpose)
    await send_verification_email(str(request.email), code)
    return {"message": "Verification code sent to email"}


# this is called immediately upon user trying to reset password but NO "new password" is asked for/received
@router.post("/verify-reset-code")
async def verify_reset_code(request: UserCompleteVerify, db: Session = Depends(get_db)):
    _, uid = await get_firebase_and_uid(email=request.email)
    verify_code(db, uid, request.code, purpose="reset")  # verify w/o deleting from DB
    return {"message": "Code verified"}


# second portion of reset password flow, user has already verified code & is now sending us the new pwd to use
@router.post("/reset-password")
async def reset_password(request: UserResetPassword, db: Session = Depends(get_db)):
    _, uid = await get_firebase_and_uid(email=request.email)
    # code gets verified a second time, consuming it this time
    verify_code(db, uid, request.code, purpose="reset", consume=True)  # delete the code after use
    try:
        auth.update_user(uid, password=request.new_password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating password: {str(e)}")
    return {"message": "Password updated successfully"}


@router.post("/verify-email")
async def verify_email(request: UserCompleteVerify, db: Session = Depends(get_db)):
    _, uid = await get_firebase_and_uid(email=request.email)
    verify_code(db, uid, request.code, purpose="verify")  # verify w/o deletion
    try:
        auth.update_user(uid, email_verified=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

    # keep this doubled/consuming AFTER Firebase checks to avoid codes being expired by Firebase errors
    verify_code(db, uid, request.code, purpose="verify", consume=True)  # verify & consume

    return {"message": "Email verified successfully"}


@router.post("/activity-ping")
def activity_ping(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.updated_at = datetime.utcnow()
    current_user.inactivity_notification_stage = None
    db.commit()
    return {"status": "ok"}
