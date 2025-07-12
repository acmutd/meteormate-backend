# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

# initialize firebase
cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # verify the firebase token
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="invalid authentication token")


async def get_firebase_user(uid: str):
    try:
        user = auth.get_user(uid)
        return user
    except Exception as e:
        raise HTTPException(status_code=404, detail="user not found")
