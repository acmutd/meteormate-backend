# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.firebase_auth import get_current_user, get_firebase_user
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # check if user already exists
    existing_user = db.query(User).filter(User.firebase_uid == current_user_token["uid"]).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="user already registered")

    # get firebase user details
    firebase_user = await get_firebase_user(current_user_token["uid"])

    # create new user
    new_user = User(
        firebase_uid=current_user_token["uid"],
        email=firebase_user.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        age=user_data.age,
        bio=user_data.bio,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user_token=Depends(get_current_user), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.firebase_uid == current_user_token["uid"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    return user
