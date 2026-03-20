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
                           Depends(security)], db: Annotated[Session, Depends(get_db)],
    request: Request
) -> User:
    try:
        # verify the firebase token
        decoded_token = auth.verify_id_token(credentials.credentials)

        # SAFETY NET - Map 'uid' to 'id' for dumb devs (myself & me)
        decoded_token["id"] = decoded_token["uid"]  # this is never used btw

        # check if user is email verified
        endpoint_func = request.scope['endpoint']
        endpoint_name = endpoint_func.__name__
        if not decoded_token["email_verified"] and (
            endpoint_name != "send_verification_code" and endpoint_name != "verify_email"
        ):
            logger.warning(f"Auth failed: Firebase user {decoded_token['uid']} email not verified")
            raise Unauthorized("Email not verified")

        user = db.query(User).filter(User.id == decoded_token["uid"]).first()
        if not user:
            logger.warning(f"Auth failed: Firebase user {decoded_token['uid']} not found in DB")
            raise Unauthorized("Invalid credentials")

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


def get_firebase_user(uid: str):
    try:
        user = auth.get_user(uid)
        return user

    except auth.UserNotFoundError:
        logger.warning(f"Requested Firebase user {uid} not found")
        raise NotFound("Firebase user")

    except Exception as e:
        logger.error(f"Error fetching Firebase user {uid}: {str(e)}", exc_info=settings.DEBUG)
        raise InternalServerError("Error fetching Firebase user")
