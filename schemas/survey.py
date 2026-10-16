# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from datetime import date, datetime

from pydantic import BaseModel, Field

from models.survey import (
    CleanlinessEnum,
    CookingFrequencyEnum,
    DealbreakerEnum,
    GuestsFrequencyEnum,
    HaveLeaseLengthEnum,
    HousingIntentEnum,
    NoiseToleranceEnum,
    NumRoommatesEnum,
    OnCampusLocationEnum,
    PetPreferenceEnum,
    RoommateClosenessEnum,
    WakeTimeEnum,
)


class SurveyCreate(BaseModel):
    housing_intent: HousingIntentEnum | None = None

    # sliders / dates
    budget_min: int | None = None
    budget_max: int | None = None
    move_in_date: date | None = None

    # wake/clean/noise
    wake_time: WakeTimeEnum | None = None
    cleanliness: CleanlinessEnum | None = None
    noise_tolerance: NoiseToleranceEnum | None = None

    # interests + dealbreakers
    interests: list[str] = Field(default_factory=list)
    dealbreakers: list[DealbreakerEnum] = Field(default_factory=list)

    # lifestyle personality
    cooking_frequency: CookingFrequencyEnum | None = None
    pet_preference: PetPreferenceEnum | None = None
    guests_frequency: GuestsFrequencyEnum | None = None
    roommate_closeness: RoommateClosenessEnum | None = None

    # on-campus
    on_campus_locations: list[OnCampusLocationEnum] = Field(default_factory=list)
    honors: bool | None = None
    llc_interest: bool | None = None
    num_roommates: NumRoommatesEnum | None = None

    # off-campus lease branch
    have_lease: bool | None = None
    have_lease_length: HaveLeaseLengthEnum | None = None

    # smoking/vaping/drinking
    smoke_vape: bool = False
    drink: bool = False


class SurveyUpdate(BaseModel):
    housing_intent: HousingIntentEnum | None = None

    # sliders / dates
    budget_min: int | None = None
    budget_max: int | None = None
    move_in_date: date | None = None

    # wake/clean/noise
    wake_time: WakeTimeEnum | None = None
    cleanliness: CleanlinessEnum | None = None
    noise_tolerance: NoiseToleranceEnum | None = None

    # interests + dealbreakers
    interests: list[str] | None = None
    dealbreakers: list[DealbreakerEnum] | None = None

    # lifestyle personality
    cooking_frequency: CookingFrequencyEnum | None = None
    pet_preference: PetPreferenceEnum | None = None
    guests_frequency: GuestsFrequencyEnum | None = None
    roommate_closeness: RoommateClosenessEnum | None = None

    # on-campus
    on_campus_locations: list[OnCampusLocationEnum] | None = None
    honors: bool | None = None
    llc_interest: bool | None = None
    num_roommates: NumRoommatesEnum | None = None

    # off-campus lease branch
    have_lease: bool | None = None
    have_lease_length: HaveLeaseLengthEnum | None = None

    # smoking/vaping/drinking
    smoke_vape: bool = False
    drink: bool = False


class SurveyResponse(BaseModel):
    user_id: str

    # core branching fields
    housing_intent: HousingIntentEnum | None = None

    # sliders / dates
    budget_min: int | None = None
    budget_max: int | None = None
    move_in_date: date | None = None

    # wake/clean/noise
    wake_time: WakeTimeEnum | None = None
    cleanliness: CleanlinessEnum | None = None
    noise_tolerance: NoiseToleranceEnum | None = None

    # interests + dealbreakers
    interests: list[str] = Field(default_factory=list)
    dealbreakers: list[DealbreakerEnum] = Field(default_factory=list)

    # lifestyle personality
    cooking_frequency: CookingFrequencyEnum | None = None
    pet_preference: PetPreferenceEnum | None = None
    guests_frequency: GuestsFrequencyEnum | None = None
    roommate_closeness: RoommateClosenessEnum | None = None

    # on-campus
    on_campus_locations: list[OnCampusLocationEnum] = Field(default_factory=list)
    honors: bool | None = None
    llc_interest: bool | None = None
    num_roommates: NumRoommatesEnum | None = None

    # off-campus
    have_lease: bool | None = None
    have_lease_length: HaveLeaseLengthEnum | None = None

    created_at: datetime
    updated_at: datetime

    # smoking/vaping/drinking
    smoke_vape: bool = False
    drink: bool = False

    class Config:
        from_attributes = True
