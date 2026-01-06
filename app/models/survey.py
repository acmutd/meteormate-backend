# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import enum

from sqlalchemy import (Column, Integer, Text, ForeignKey, Date, DateTime, Boolean, text)
from sqlalchemy import Enum as PGEnum
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# Shared housing enums
class LeaseLengthEnum(str, enum.Enum):
    SEMESTER = "semester"
    ACADEMIC = "academic"
    YEAR = "year"


class HousingIntentEnum(str, enum.Enum):
    ON_CAMPUS = "on_campus"
    OFF_CAMPUS = "off_campus"
    BOTH = "both"


# Wake/Clean/Noise tile enums
class WakeTimeEnum(str, enum.Enum):
    EARLY_BIRD = "early_bird"
    FLEXIBLE = "flexible"
    NIGHT_OWL = "night_owl"


class CleanlinessEnum(str, enum.Enum):
    RELAXED = "relaxed"
    TIDY = "tidy"
    NEAT_FREAK = "neat_freak"


class NoiseToleranceEnum(str, enum.Enum):
    QUIET = "quiet"
    MODERATE = "moderate"
    LOUD = "loud"


# Lifestyle tile enums
class CookingFrequencyEnum(str, enum.Enum):
    NEVER = "never"
    RARELY = "rarely"
    OFTEN = "often"


class PetPreferenceEnum(str, enum.Enum):
    OKAY = "okay"
    NOT_OKAY = "not_okay"
    HAVE_A_PET = "have_a_pet"


class GuestsFrequencyEnum(str, enum.Enum):
    NEVER = "never"
    SOMETIMES = "sometimes"
    OFTEN = "often"


class RoommateClosenessEnum(str, enum.Enum):
    NOT_CLOSE = "not_close"
    FRIENDS = "friends"
    CLOSE_FRIENDS = "close_friends"


# Dealbreakers
class DealbreakerEnum(str, enum.Enum):
    SMOKE_VAPE = "smoke_vape"
    DRINK = "drink"
    SAME_GENDER = "same_gender"


# On-campus flow
class OnCampusLocationEnum(str, enum.Enum):
    UV = "uv"
    CC = "cc"
    FRESHMAN_DORMS = "freshman_dorms"
    NORTHSIDE = "northside"


class NumRoommatesEnum(str, enum.Enum):
    NO_PREFERENCE = "no_preference"
    ONE = "one"
    TWO = "two"
    THREE = "three"


# Off-campus "have a lease" flow
class HaveLeaseLengthEnum(str, enum.Enum):
    SEMESTER = "semester"
    ACADEMIC_YEAR = "academic_year"
    YEAR = "year"


class Survey(Base):
    __tablename__ = "surveys"

    user_id = Column(
        Text,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    # Core housing fields
    housing_intent = Column(PGEnum(HousingIntentEnum, name="housing_intent_enum"), nullable=True)

    # Sliders (rent/budget)
    budget_min = Column(Integer, nullable=True)
    budget_max = Column(Integer, nullable=True)

    move_in_date = Column(Date, nullable=True)
    lease_length = Column(PGEnum(LeaseLengthEnum, name="lease_length_enum"), nullable=True)

    # Wake/Clean/Noise
    wake_time = Column(PGEnum(WakeTimeEnum, name="wake_time_enum"), nullable=True)
    cleanliness = Column(PGEnum(CleanlinessEnum, name="cleanliness_enum"), nullable=True)
    noise_tolerance = Column(PGEnum(NoiseToleranceEnum, name="noise_tolerance_enum"), nullable=True)

    # Interests
    interests = Column(ARRAY(Text), nullable=False, server_default="{}")

    # Dealbreakers
    dealbreakers = Column(
        ARRAY(PGEnum(DealbreakerEnum, name="dealbreaker_enum")),
        nullable=False,
        server_default="{}",
    )

    # Lifestyle Personality
    cooking_frequency = Column(
        PGEnum(CookingFrequencyEnum, name="cooking_frequency_enum"), nullable=True
    )
    pet_preference = Column(PGEnum(PetPreferenceEnum, name="pet_preference_enum"), nullable=True)
    guests_frequency = Column(
        PGEnum(GuestsFrequencyEnum, name="guests_frequency_enum"), nullable=True
    )
    roommate_closeness = Column(
        PGEnum(RoommateClosenessEnum, name="roommate_closeness_enum"), nullable=True
    )

    # On-campus flow
    on_campus_locations = Column(
        ARRAY(PGEnum(OnCampusLocationEnum, name="on_campus_location_enum")),
        nullable=False,
        server_default="{}",
    )
    # asked on on-campus page
    honors = Column(Boolean, nullable=True)

    # only relevant if freshman_dorms selected
    llc_interest = Column(Boolean, nullable=True)

    # relevant for UV/CC/Northside
    num_roommates = Column(PGEnum(NumRoommatesEnum, name="num_roommates_enum"), nullable=True)

    # Off-campus lease flow
    have_lease = Column(Boolean, nullable=True)
    have_lease_length = Column(
        PGEnum(HaveLeaseLengthEnum, name="have_lease_length_enum"), nullable=False
    )

    # Catch-all for any future screens/edge fields
    answers = Column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="survey", uselist=False)
