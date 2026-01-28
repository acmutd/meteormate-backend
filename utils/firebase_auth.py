# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import logging

import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings

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
        logger.critical(f"Failed to initialize Firebase Admin SDK: {str(e)}")
        raise

security = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials == settings.ADMIN_BEARER:
        if not settings.DEBUG:
            raise HTTPException(status_code=403,
                                detail="Admin bypass only in DEBUG mode")
        return {"id": settings.ADMIN_UID, "uid": settings.ADMIN_UID}

    try:
        # verify the firebase token
        decoded_token = auth.verify_id_token(credentials.credentials)

        # SAFETY NET - Map 'uid' to 'id' for dumb devs (myself)
        decoded_token["id"] = decoded_token["uid"]

        return decoded_token

    except auth.ExpiredIdTokenError:
        logger.warning("Auth failed: Token Expired")
        raise HTTPException(status_code=401,
                            detail="Firebase token has expired")
    except auth.RevokedIdTokenError:
        logger.warning("Auth failed: Token Revoked")
        raise HTTPException(status_code=401,
                            detail="Firebase token has been revoked")
    except auth.InvalidIdTokenError as e:
        logger.warning(f"Auth failed: Invalid Token - {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token")
    except Exception as e:
        logger.error(f"Unexpected authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication error")


async def get_firebase_user(uid: str):
    try:
        user = auth.get_user(uid)
        return user
    except auth.UserNotFoundError:
        logger.warning(f"Requested Firebase user {uid} not found")
        raise HTTPException(status_code=404, detail="Firebase user not found")
    except Exception as e:
        logger.error(f"Error fetching Firebase user {uid}: {str(e)}")
        raise HTTPException(status_code=500,
                            detail="Error fetching Firebase user")
