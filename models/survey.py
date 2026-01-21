# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import enum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


def mm_enum(enum_cls: type[enum.Enum], name: str) -> SAEnum:
    return SAEnum(enum_cls, name=name, values_callable=lambda e: [x.value for x in e])


# Shared housing enums
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
    housing_intent = Column(mm_enum(HousingIntentEnum, "housing_intent_enum"), nullable=True)

    # Sliders (rent/budget)
    budget_min = Column(Integer, nullable=True)
    budget_max = Column(Integer, nullable=True)

    move_in_date = Column(Date, nullable=True)

    # Wake/Clean/Noise
    wake_time = Column(mm_enum(WakeTimeEnum, "wake_time_enum"), nullable=True)
    cleanliness = Column(mm_enum(CleanlinessEnum, "cleanliness_enum"), nullable=True)
    noise_tolerance = Column(mm_enum(NoiseToleranceEnum, "noise_tolerance_enum"), nullable=True)

    # Interests
    interests = Column(ARRAY(Text), nullable=False, server_default="{}")

    # Dealbreakers
    dealbreakers = Column(
        ARRAY(mm_enum(DealbreakerEnum, "dealbreaker_enum")),
        nullable=False,
        server_default="{}",
    )

    # Lifestyle / Personality
    cooking_frequency = Column(
        mm_enum(CookingFrequencyEnum, "cooking_frequency_enum"), nullable=True
    )
    pet_preference = Column(mm_enum(PetPreferenceEnum, "pet_preference_enum"), nullable=True)
    guests_frequency = Column(mm_enum(GuestsFrequencyEnum, "guests_frequency_enum"), nullable=True)
    roommate_closeness = Column(
        mm_enum(RoommateClosenessEnum, "roommate_closeness_enum"), nullable=True
    )

    # On-campus flow
    on_campus_locations = Column(
        ARRAY(mm_enum(OnCampusLocationEnum, "on_campus_location_enum")),
        nullable=False,
        server_default="{}",
    )

    # asked on on-campus page
    honors = Column(Boolean, nullable=True)

    llc_interest = Column(Boolean, nullable=True)

    # UV/CC/Northside stuff
    num_roommates = Column(mm_enum(NumRoommatesEnum, "num_roommates_enum"), nullable=True)

    # Off-campus lease flow
    have_lease = Column(Boolean, nullable=True)
    have_lease_length = Column(
        mm_enum(HaveLeaseLengthEnum, "have_lease_length_enum"), nullable=True
    )

    # Catch-all
    answers = Column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    smoke_vape = Column(Boolean, nullable=False, server_default=text("false"))
    drink = Column(Boolean, nullable=False, server_default=text("false"))

    user = relationship("User", back_populates="survey", uselist=False)
