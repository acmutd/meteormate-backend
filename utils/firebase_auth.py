# Created by Ryan Polasky | 7/12/25
# Updated by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

import logging
from typing import Annotated

import firebase_admin
from firebase_admin import credentials, auth
from sqlalchemy.orm import Session
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings
from database import get_db
from models.admin import Admins, Banlist
from models.user import User
from utils.exceptions import InternalServerError, NotFound, Unauthorized

logger = logging.getLogger("meteormate." + __name__)

# noinspection PyProtectedMember
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(
            cred,
            {
                "storageBucket": settings.FIREBASE_STORAGE_BUCKET,
            },
        )
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.critical(
            f"Failed to initialize Firebase Admin SDK: {str(e)}",
            exc_info=settings.DEBUG,
        )
        raise

security = HTTPBearer()


# more reason to hate YAPF
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials,
                           Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        # verify the firebase token
        decoded_token = auth.verify_id_token(credentials.credentials)

        # SAFETY NET - Map 'uid' to 'id' for dumb devs (myself & me)
        decoded_token["id"] = decoded_token["uid"]  # this is never used btw

        user = db.query(User).filter(User.id == decoded_token["uid"]).first()
        if not user:
            logger.warning(f"Auth failed: Firebase user {decoded_token['uid']} not found in DB")
            raise Unauthorized("Invalid credentials")

        banned = (db.query(Banlist).filter(Banlist.user_id == decoded_token["uid"]).first())
        if banned:
            logger.warning(f"Auth failed: User {decoded_token['uid']} is banned")
            raise Unauthorized("Your account has been banned")

        return user

    except auth.ExpiredIdTokenError:
        logger.warning("Auth failed: Token Expired")
        raise Unauthorized("Firebase token has expired")

    except auth.RevokedIdTokenError:
        logger.warning("Auth failed: Token Revoked")
        raise Unauthorized("Firebase token has been revoked")

    except auth.InvalidIdTokenError as e:
        logger.warning(f"Auth failed: Invalid Token - {str(e)}")
        raise Unauthorized("Invalid Firebase token")

    except Exception as e:
        if isinstance(e, (Unauthorized)):
            raise

        logger.error(f"Unexpected authentication error: {str(e)}", exc_info=settings.DEBUG)
        raise Unauthorized("Authentication error")


def ensure_email_verified(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.email_verified:
        logger.warning(f"Email verification failed for User {current_user.id}")
        raise Unauthorized("Email verification required")

    return current_user


async def ensure_admin(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        admin = db.query(Admins).filter(Admins.net_id == current_user.utd_id).first()

        if not admin:
            logger.warning(f"Admin check failed: User {current_user.id} is not an admin")
            raise Unauthorized("Admin privileges required")

    except Exception as e:
        logger.error(f"Unexpected error during admin check: {str(e)}", exc_info=settings.DEBUG)
        raise Unauthorized("Authentication error")


def get_firebase_user(uid: str = None, email: str = None) -> auth.UserRecord:
    """
    Fetches a Firebase user by UID or email. At least one of uid or email must be provided.
    Args:
        - uid: The UID of the Firebase user to fetch
        - email: The email of the Firebase user to fetch
    Returns:
        - user: auth.UserRecord object representing the Firebase user
    Raises:
        - ValueError: If neither uid nor email is provided
        - NotFound: If no Firebase user is found with the provided uid or email
        - InternalServerError: If there is an error fetching the Firebase user
    """
    if not uid and not email:
        logger.warning("get_firebase_user called without uid or email")
        raise ValueError("Must provide either uid or email to fetch Firebase user")

    try:
        if uid:
            user = auth.get_user(uid)
            return user
        elif email:
            user = auth.get_user_by_email(email)
            return user

    except auth.UserNotFoundError:
        logger.warning(f"Requested Firebase user {uid} not found")
        raise NotFound("Firebase user")

    except Exception as e:
        logger.error(f"Error fetching Firebase user {uid}: {str(e)}", exc_info=settings.DEBUG)
        raise InternalServerError("Error fetching Firebase user")
