# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from datetime import datetime, date
from typing import Optional, List, Dict, Any

from pydantic import BaseModel

from app.models.survey import (
    HousingIntentEnum,
    WakeTimeEnum,
    CleanlinessEnum,
    NoiseToleranceEnum,
    CookingFrequencyEnum,
    PetPreferenceEnum,
    GuestsFrequencyEnum,
    RoommateClosenessEnum,
    OnCampusLocationEnum,
    NumRoommatesEnum,
    HaveLeaseLengthEnum,
    DealbreakerEnum,
)


class SurveyCreate(BaseModel):
    housing_intent: Optional[HousingIntentEnum] = None

    # sliders / dates
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    move_in_date: Optional[date] = None

    # wake/clean/noise
    wake_time: Optional[WakeTimeEnum] = None
    cleanliness: Optional[CleanlinessEnum] = None
    noise_tolerance: Optional[NoiseToleranceEnum] = None

    # interests + dealbreakers
    interests: List[str] = []
    dealbreakers: List[DealbreakerEnum] = []

    # lifestyle personality
    cooking_frequency: Optional[CookingFrequencyEnum] = None
    pet_preference: Optional[PetPreferenceEnum] = None
    guests_frequency: Optional[GuestsFrequencyEnum] = None
    roommate_closeness: Optional[RoommateClosenessEnum] = None

    # on-campus
    on_campus_locations: List[OnCampusLocationEnum] = []
    honors: Optional[bool] = None
    llc_interest: Optional[bool] = None
    num_roommates: Optional[NumRoommatesEnum] = None

    # off-campus lease branch
    have_lease: Optional[bool] = None
    have_lease_length: HaveLeaseLengthEnum

    # catch all
    answers: Dict[str, Any] = {}


class SurveyUpdate(BaseModel):
    housing_intent: Optional[HousingIntentEnum] = None

    # sliders / dates
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    move_in_date: Optional[date] = None

    # wake/clean/noise
    wake_time: Optional[WakeTimeEnum] = None
    cleanliness: Optional[CleanlinessEnum] = None
    noise_tolerance: Optional[NoiseToleranceEnum] = None

    # interests + dealbreakers
    interests: Optional[List[str]] = None
    dealbreakers: Optional[List[DealbreakerEnum]] = None

    # lifestyle personality
    cooking_frequency: Optional[CookingFrequencyEnum] = None
    pet_preference: Optional[PetPreferenceEnum] = None
    guests_frequency: Optional[GuestsFrequencyEnum] = None
    roommate_closeness: Optional[RoommateClosenessEnum] = None

    # on-campus
    on_campus_locations: Optional[List[OnCampusLocationEnum]] = None
    honors: Optional[bool] = None
    llc_interest: Optional[bool] = None
    num_roommates: Optional[NumRoommatesEnum] = None

    # off-campus lease branch
    have_lease: Optional[bool] = None
    have_lease_length: Optional[HaveLeaseLengthEnum] = None

    # catch all
    answers: Optional[Dict[str, Any]] = None


class SurveyResponse(BaseModel):
    user_id: str

    # core branching fields
    housing_intent: Optional[HousingIntentEnum] = None

    # sliders / dates
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    move_in_date: Optional[date] = None

    # wake/clean/noise
    wake_time: Optional[WakeTimeEnum] = None
    cleanliness: Optional[CleanlinessEnum] = None
    noise_tolerance: Optional[NoiseToleranceEnum] = None

    # interests + dealbreakers
    interests: List[str] = []
    dealbreakers: List[DealbreakerEnum] = []

    # lifestyle personality
    cooking_frequency: Optional[CookingFrequencyEnum] = None
    pet_preference: Optional[PetPreferenceEnum] = None
    guests_frequency: Optional[GuestsFrequencyEnum] = None
    roommate_closeness: Optional[RoommateClosenessEnum] = None

    # on-campus
    on_campus_locations: List[OnCampusLocationEnum] = []
    honors: Optional[bool] = None
    llc_interest: Optional[bool] = None
    num_roommates: Optional[NumRoommatesEnum] = None

    # off-campus
    have_lease: Optional[bool] = None
    have_lease_length: HaveLeaseLengthEnum

    # catch all
    answers: Dict[str, Any] = {}

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
