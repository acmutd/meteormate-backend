# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SurveyCreate(BaseModel):
    housing_type: str
    budget_min: int
    budget_max: int
    move_in_date: datetime
    lease_length: str
    cleanliness_level: int
    noise_level: int
    guests_frequency: str
    study_habits: str
    sleep_schedule: str
    interests: List[str]
    personality_traits: dict
    deal_breakers: List[str]


class SurveyUpdate(BaseModel):
    housing_type: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    move_in_date: Optional[datetime] = None
    lease_length: Optional[str] = None
    cleanliness_level: Optional[int] = None
    noise_level: Optional[int] = None
    guests_frequency: Optional[str] = None
    study_habits: Optional[str] = None
    sleep_schedule: Optional[str] = None
    interests: Optional[List[str]] = None
    personality_traits: Optional[dict] = None
    deal_breakers: Optional[List[str]] = None


class SurveyResponse(BaseModel):
    id: int
    user_id: str
    housing_type: str
    budget_min: int
    budget_max: int
    move_in_date: datetime
    lease_length: str
    cleanliness_level: int
    noise_level: int
    guests_frequency: str
    study_habits: str
    sleep_schedule: str
    interests: List[str]
    personality_traits: dict
    deal_breakers: List[str]
    ai_summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True