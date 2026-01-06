# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import random
import logging
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

logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse)
async def register_user(
        user_data: UserCreate,
        db: Session = Depends(get_db),
):
    # check if net id is already taken
    existing_utd_user = db.query(User).filter(User.utd_id == user_data.utd_id).first()

    if existing_utd_user:
        # only log Firebase UID, not PII (this applies to all relevant logs)
        logger.warning(f"STATUS 400 - Account with Firebase UID {existing_utd_user.id} already exists in \"User\" database")
        raise HTTPException(status_code=400, detail="Account already exists")
    logger.info(f"Success - No existing user with Firebase UID {existing_utd_user.id} in \"User\" database")

    # check if email is already taken
    existing_email_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_email_user:
        logger.warning(f"STATUS 400 - Account with Firebase UID {existing_email_user.id} already exists in \"User\" database")
        raise HTTPException(status_code=400, detail="Account already exists")
    logger.info(f"Success - No existing user with Firebase UID {existing_email_user.id} already exists in \"User\" database")

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
        
        logger.info(f"Successfully created User with Firebase UID - {new_user.id}")

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"Successfully committed new User with Firebase UID {new_user.id} to \"User\" and Firebase databases")

        return new_user

    except auth.EmailAlreadyExistsError:
        logger.warning(f"STATUS 400 - Email from User with Firebase UID {new_user.id} already exists in \"User\" and Firebase databases")
        raise HTTPException(status_code=400, detail="Account already exists")
    except Exception as e:
        db.rollback()
        # if database creation failed but Firebase user was created, clean up
        try:
            if 'firebase_user' in locals():
                logger.critical(f"Database creation failed, but User with Firebase UID {firebase_user.uid} was still created - cleaning up by deleting that Firebase user")
                auth.delete_user(firebase_user.uid)
        except:
            pass
        logger.error(f"STATUS 500 - The following error occured when creating the new User and adding it to the \"User\" and Firebase databases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
        current_user_token=Depends(get_current_user),
        db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        logger.warning(f"STATUS 404 - User with Firebase UID {current_user_token.get("uid")} not found in \"User\" database")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Successfully found User with Firebase UID {current_user_token.get("uid")} in \"User\" database")
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
            logger.info(f"Successfully found User with Firebase UID {uid} in the Firebase database")
        else:
            firebase_user = auth.get_user_by_email(email_str)
            logger.info(f"Successfully found User with Firebase UID {firebase_user.uid} in the Firebase database")
    except auth.UserNotFoundError:
        if request.uid:
            logger.warning(f"STATUS 404 - User with Firebase UID {request.uid} not found in the Firebase database")
        else:
            # Once again, avoiding leaking PII
            logger.warning(f"STATUS 404 - User not found in the Firebase database")
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"STATUS 500 - The following error occurred when trying to fetch the User from the Firebase database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

    # Only block if this is for signup email verification
    if request.purpose == "verify" and firebase_user.email_verified:
        logger.warning(f"STATUS 400 - User with Firebase UID {firebase_user.uid} already verified in Firebase database")
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
    logger.info(f"Successfully sent verification code to email for User with Firebase UID {uid}")

    return {"message": "Verification code sent to email"}


@router.post("/verify-reset-code")
async def verify_reset_code(request: UserCompleteVerify):
    email_str = str(request.email)
    try:
        firebase_user = auth.get_user_by_email(email_str)
        uid = firebase_user.uid
        logger.info(f"Successfully found user with Firebase UID {uid} in the Firebase database")
    except auth.UserNotFoundError:
        logger.warning(f"STATUS 404 - User not found in the Firebase database")
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"STATUS 500 - The following error occurred when trying to fetch the User: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

    stored_code = verification_codes.get(uid)
    if not stored_code:
        logger.warning(f"STATUS 400 - Verification code for User with Firebase UID {uid} not found in the expiring verification_codes cache")
        raise HTTPException(status_code=400, detail="No verification code found")

    if stored_code != request.code:
        logger.warning(f"STATUS 400 - Verification code {request.code} entered by User with Firebase UID {uid} does not match the stored verification code {stored_code}")
        raise HTTPException(status_code=400, detail="Invalid verification code")

    return {"message": "Code verified"}


@router.post("/reset-password")
async def reset_password(request: UserResetPassword):
    """Reset password using email + 6-digit code"""

    email_str = str(request.email)

    try:
        firebase_user = auth.get_user_by_email(email_str)
        uid = firebase_user.uid
        logger.info(f"Successfully found user with Firebase UID {uid} in the Firebase database")
    except auth.UserNotFoundError:
        logger.warning(f"STATUS 404 - User not found in the Firebase database")
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"STATUS 500 - The following error occurred when trying to fetch the User: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

    stored_code = verification_codes.get(uid)
    if not stored_code:
        logger.warning(f"STATUS 400 - Verification code for User with Firebase UID {uid} not found in the expiring verification_codes cache")
        raise HTTPException(status_code=400, detail="No verification code found")
    if stored_code != request.code:
        logger.warning(f"STATUS 400 - Verification code {request.code} entered by User with Firebase UID {uid} does not match the stored verification code {stored_code}")
        raise HTTPException(status_code=400, detail="Invalid verification code")
    logger.info(f"Successfully found the stored verification code for User with Firebase UID {uid} in the expiring verification_codes cache")

    try:
        auth.update_user(uid, password=request.new_password)
        logger.info(f"Successfully updated password for User with Firebase UID {uid} in the Firebase database")
    except Exception as e:
        logger.error(f"STATUS 500 - The following error occurred when trying to update the password for User with Firebase UID {uid}: {str(e)}")
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
        logger.warning(f"STATUS 404 - User not found in the Firebase database")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Successfully found user with Firebase UID {uid} in the Firebase database")

    # get code from memory
    stored_code = verification_codes.get(uid)

    if not stored_code:
        logger.warning(f"STATUS 400 - Verification code for User with Firebase UID {uid} not found in the expiring verification_codes cache")
        raise HTTPException(status_code=400, detail="No verification code found")
    logger.info(f"Successfully found stored verification code for user with Firebase UID {uid} in the expiring verification_codes cache")

    # check if code matches
    if stored_code != request.code:
        logger.warning(f"STATUS 400 - Verification code {request.code} entered by User with Firebase UID {uid} does not match the stored verification code {stored_code}")
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # mark email as verified in Firebase
    try:
        auth.update_user(uid, email_verified=True)
        logger.info(f"Successfully verified User with Firebase UID {uid} in the Firebase database")
    except Exception as e:
        logger.error(f"STATUS 500 - The following error occurred when trying to complete verification of User with Firebase UID {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

    # Delete code after successful verification
    del verification_codes[uid]
    logger.info(f"Successfully deleted temporary verification code for User with Firebase UID {uid} from the expiring verification_codes cache")

    return {"message": "Email verified successfully"}
