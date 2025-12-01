# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from firebase_admin import auth

from app.database import get_db
from app.models.user import User, UserRequestVerify, UserCompleteVerify, UserResetPassword
from app.utils.firebase_auth import get_current_user, get_firebase_user, verification_codes
from app.utils.email import send_verification_email
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(
        user_data: UserCreate,
        db: Session = Depends(get_db),
):
    # check if net id is already taken
    existing_utd_user = db.query(User).filter(User.utd_id == user_data.utd_id).first()
    if existing_utd_user:
        raise HTTPException(status_code=400, detail="Account already exists")

    # check if email is already taken
    existing_email_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_email_user:
        raise HTTPException(status_code=400, detail="Account already exists")

    try:
        # create Firebase user
        firebase_user = auth.create_user(
            email=user_data.email,
            password=user_data.password,
            email_verified=False
        )

        # create user in db
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
        # if database creation failed but Firebase user was created, clean up
        try:
            if 'firebase_user' in locals():
                auth.delete_user(firebase_user.uid)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
        current_user_token=Depends(get_current_user),
        db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/send-verification-code")
async def send_verification_code(
        request: UserRequestVerify,
):
    """Send 6-digit verification code to user's email"""

    email_str = str(request.email)

    try:
        if request.uid:
            firebase_user = await get_firebase_user(request.uid)
        else:
            firebase_user = auth.get_user_by_email(email_str)
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

    # Only block if this is for signup email verification
    if request.purpose == "verify" and firebase_user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    # (optional) For reset, you *might* want the opposite:
    # if request.purpose == "reset" and not firebase_user.email_verified:
    #     raise HTTPException(status_code=400, detail="Email not verified yet")

    code = str(random.randint(100000, 999999))
    uid = firebase_user.uid
    verification_codes[uid] = code

    await send_verification_email(
        email_str,
        code,
        firebase_user.display_name or "User"
    )

    return {"message": "Verification code sent to email"}


@router.post("/verify-reset-code")
async def verify_reset_code(request: UserCompleteVerify):
    email_str = str(request.email)
    try:
        firebase_user = auth.get_user_by_email(email_str)
        uid = firebase_user.uid
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

    stored_code = verification_codes.get(uid)
    if not stored_code:
        raise HTTPException(status_code=400, detail="No verification code found")

    if stored_code != request.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    return {"message": "Code verified"}


@router.post("/reset-password")
async def reset_password(request: UserResetPassword):
    """Reset password using email + 6-digit code"""

    email_str = str(request.email)

    try:
        firebase_user = auth.get_user_by_email(email_str)
        uid = firebase_user.uid
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

    stored_code = verification_codes.get(uid)
    if not stored_code:
        raise HTTPException(status_code=400, detail="No verification code found")
    if stored_code != request.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    try:
        auth.update_user(uid, password=request.new_password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating password: {str(e)}")

    del verification_codes[uid]

    return {"message": "Password updated successfully"}


@router.post("/verify-email")
async def verify_email(
        request: UserCompleteVerify
):
    """Verify email using 6-digit code"""

    # get Firebase user by email to get UID
    try:
        firebase_user = auth.get_user_by_email(request.email)
        uid = firebase_user.uid
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

    # get code from memory
    stored_code = verification_codes.get(uid)

    if not stored_code:
        raise HTTPException(status_code=400, detail="No verification code found")

    # check if code matches
    if stored_code != request.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # mark email as verified in Firebase
    try:
        auth.update_user(uid, email_verified=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

    # Delete code after successful verification
    del verification_codes[uid]

    return {"message": "Email verified successfully"}
