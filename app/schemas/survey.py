# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.survey import (
    HousingTypeEnum, LeaseLengthEnum, GuestsFrequencyEnum, StudyHabitsEnum, SleepScheduleEnum,
    CookingFrequencyEnum, PetPreferenceEnum, RoomateClosenessEnum, HousingLocationEnum, HonorsEnum,
    LLCEnum, HaveALeaseEnum, NumOfRoomatesEnum, DontHaveALeaseEnum
)


class SurveyCreate(BaseModel):
    housing_type: List[HousingTypeEnum]
    lease_length: List[LeaseLengthEnum]
    guests_frequency: List[GuestsFrequencyEnum]
    study_habits: List[StudyHabitsEnum]

    cooking_frequency: CookingFrequencyEnum
    pet_preference: PetPreferenceEnum
    roomate_closseness: RoomateClosenessEnum
    housing_location: HousingLocationEnum
    honors: HonorsEnum
    llc: LLCEnum
    have_a_lease: HaveALeaseEnum
    num_of_roomates: NumOfRoomatesEnum
    dont_have_a_lease: DontHaveALeaseEnum

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

    cooking_frequency: CookingFrequencyEnum = None
    pet_preference: PetPreferenceEnum = None
    roomate_closseness: RoomateClosenessEnum = None
    housing_location: HousingLocationEnum = None
    honors: HonorsEnum = None
    llc: LLCEnum = None
    have_a_lease: HaveALeaseEnum = None
    num_of_roomates: NumOfRoomatesEnum = None
    dont_have_a_lease: DontHaveALeaseEnum = None

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

    cooking_frequency: CookingFrequencyEnum
    pet_preference: PetPreferenceEnum
    roomate_closseness: RoomateClosenessEnum
    housing_location: HousingLocationEnum
    honors: HonorsEnum
    llc: LLCEnum
    have_a_lease: HaveALeaseEnum
    num_of_roomates: NumOfRoomatesEnum
    dont_have_a_lease: DontHaveALeaseEnum

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
