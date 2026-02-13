# Created by Ryan Polasky | 7/12/25
# Updated by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

import logging

import firebase_admin
from firebase_admin import credentials, auth
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings
from database import get_db
from models.user import User
from utils.exceptions import Forbidden, InternalServerError, NotFound, Unauthorized

logger = logging.getLogger("meteormate." + __name__)

# noinspection PyProtectedMember
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred, {
            'storageBucket': settings.FIREBASE_STORAGE_BUCKET,
        })
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.critical(
            f"Failed to initialize Firebase Admin SDK: {str(e)}", exc_info=settings.DEBUG
        )
        raise

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    if credentials.credentials == settings.ADMIN_BEARER:
        if not settings.DEBUG:
            raise Forbidden("Admin bypass only in DEBUG mode")

        user = db.query(User).filter(User.id == settings.ADMIN_UID).first()
        return {"id": settings.ADMIN_UID, "uid": settings.ADMIN_UID}, user

    try:
        # verify the firebase token
        decoded_token = auth.verify_id_token(credentials.credentials)

        # SAFETY NET - Map 'uid' to 'id' for dumb devs (myself & me)
        decoded_token["id"] = decoded_token["uid"]  # this is never used btw

        user = db.query(User).filter(User.id == decoded_token["uid"]).first()
        if not user:
            logger.warning(f"Auth failed: Firebase user {decoded_token['uid']} not found in DB")
            raise NotFound("User")

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
        logger.error(f"Unexpected authentication error: {str(e)}", exc_info=settings.DEBUG)
        raise Unauthorized("Authentication error")


async def get_firebase_user(uid: str):
    try:
        user = auth.get_user(uid)
        return user

    except auth.UserNotFoundError:
        logger.warning(f"Requested Firebase user {uid} not found")
        raise NotFound("Firebase user")

    except Exception as e:
        logger.error(f"Error fetching Firebase user {uid}: {str(e)}", exc_info=settings.DEBUG)
        raise InternalServerError("Error fetching Firebase user")


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
        raise NotFound("User")
    except Exception as e:
        logger.error(str(e), exc_info=settings.DEBUG)
        raise InternalServerError("Error fetching user")
