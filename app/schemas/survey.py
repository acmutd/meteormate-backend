# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.survey import (
    HousingTypeEnum, LeaseLengthEnum, GuestsFrequencyEnum, StudyHabitsEnum, SleepScheduleEnum
)


class SurveyCreate(BaseModel):
    housing_type: List[HousingTypeEnum]
    lease_length: List[LeaseLengthEnum]
    guests_frequency: List[GuestsFrequencyEnum]
    study_habits: List[StudyHabitsEnum]

    sleep_schedule: SleepScheduleEnum

    budget_min: int
    budget_max: int
    move_in_date: datetime
    cleanliness_level: int
    noise_level: int
    interests: List[str]
    personality_traits: dict
    deal_breakers: List[str]


class SurveyUpdate(BaseModel):
    housing_type: Optional[List[HousingTypeEnum]] = None
    lease_length: Optional[List[LeaseLengthEnum]] = None
    guests_frequency: Optional[List[GuestsFrequencyEnum]] = None
    study_habits: Optional[List[StudyHabitsEnum]] = None
    sleep_schedule: Optional[SleepScheduleEnum] = None

    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    move_in_date: Optional[datetime] = None
    cleanliness_level: Optional[int] = None
    noise_level: Optional[int] = None
    interests: Optional[List[str]] = None
    personality_traits: Optional[dict] = None
    deal_breakers: Optional[List[str]] = None


class SurveyResponse(BaseModel):
    id: int
    user_id: str
    housing_type: List[HousingTypeEnum]
    lease_length: List[LeaseLengthEnum]
    guests_frequency: List[GuestsFrequencyEnum]
    study_habits: List[StudyHabitsEnum]
    sleep_schedule: SleepScheduleEnum

    budget_min: int
    budget_max: int
    move_in_date: datetime
    cleanliness_level: int
    noise_level: int
    interests: List[str]
    personality_traits: dict
    deal_breakers: List[str]
    ai_summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
