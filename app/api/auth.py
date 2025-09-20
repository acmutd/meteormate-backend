# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User
from app.utils.firebase_auth import get_current_user, get_firebase_user
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token["id"]

    existing_user = db.query(User).filter(User.id == uid).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")

    firebase_user = await get_firebase_user(uid)

    new_user = User(
        id=uid,
        email=getattr(firebase_user, "email", None),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        birthdate=user_data.birthdate,
        utd_id=user_data.utd_id,
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflict creating user") from e

    db.refresh(new_user)
    return new_user


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token["id"]
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
