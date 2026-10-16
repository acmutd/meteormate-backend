# Created by Ryan Polasky | 7/12/25
# Updated by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import ORMBase, enum_values

if TYPE_CHECKING:
    from models.user import User


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


class Survey(ORMBase):
    __tablename__ = "surveys"

    user_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    # Core housing fields
    housing_intent: Mapped[HousingIntentEnum] = mapped_column(
        SQLEnum(
            HousingIntentEnum, name="housing_intent_enum", values_callable=enum_values
        ),
        nullable=True,
    )

    # Sliders (rent/budget)
    budget_min: Mapped[int] = mapped_column(Integer, nullable=True)
    budget_max: Mapped[int] = mapped_column(Integer, nullable=True)

    move_in_date: Mapped[date] = mapped_column(Date, nullable=True)

    # Wake/Clean/Noise
    wake_time: Mapped[WakeTimeEnum] = mapped_column(
        SQLEnum(WakeTimeEnum, name="wake_time_enum", values_callable=enum_values),
        nullable=True,
    )
    cleanliness: Mapped[CleanlinessEnum] = mapped_column(
        SQLEnum(CleanlinessEnum, name="cleanliness_enum", values_callable=enum_values),
        nullable=True,
    )
    noise_tolerance: Mapped[NoiseToleranceEnum] = mapped_column(
        SQLEnum(
            NoiseToleranceEnum, name="noise_tolerance_enum", values_callable=enum_values
        ),
        nullable=True,
    )

    # Interests
    interests: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default="{}"
    )

    # Dealbreakers
    dealbreakers: Mapped[DealbreakerEnum] = mapped_column(
        ARRAY(
            SQLEnum(
                DealbreakerEnum, name="dealbreaker_enum", values_callable=enum_values
            )
        ),
        nullable=False,
        server_default="{}",
    )

    # Lifestyle / Personality
    cooking_frequency: Mapped[CookingFrequencyEnum] = mapped_column(
        SQLEnum(
            CookingFrequencyEnum,
            name="cooking_frequency_enum",
            values_callable=enum_values,
        ),
        nullable=True,
    )
    pet_preference: Mapped[PetPreferenceEnum] = mapped_column(
        SQLEnum(
            PetPreferenceEnum, name="pet_preference_enum", values_callable=enum_values
        ),
        nullable=True,
    )
    guests_frequency: Mapped[GuestsFrequencyEnum] = mapped_column(
        SQLEnum(
            GuestsFrequencyEnum,
            name="guests_frequency_enum",
            values_callable=enum_values,
        ),
        nullable=True,
    )
    roommate_closeness: Mapped[RoommateClosenessEnum] = mapped_column(
        SQLEnum(
            RoommateClosenessEnum,
            name="roommate_closeness_enum",
            values_callable=enum_values,
        ),
        nullable=True,
    )

    # On-campus flow
    on_campus_locations: Mapped[OnCampusLocationEnum] = mapped_column(
        ARRAY(
            SQLEnum(
                OnCampusLocationEnum,
                name="on_campus_location_enum",
                values_callable=enum_values,
            )
        ),
        nullable=False,
        server_default="{}",
    )

    # asked on on-campus page
    honors: Mapped[bool] = mapped_column(Boolean, nullable=True)

    llc_interest: Mapped[bool] = mapped_column(Boolean, nullable=True)

    # UV/CC/Northside stuff
    num_roommates: Mapped[NumRoommatesEnum] = mapped_column(
        SQLEnum(
            NumRoommatesEnum, name="num_roommates_enum", values_callable=enum_values
        ),
        nullable=True,
    )

    # Off-campus lease flow
    have_lease: Mapped[bool] = mapped_column(Boolean, nullable=True)
    have_lease_length: Mapped[HaveLeaseLengthEnum] = mapped_column(
        SQLEnum(
            HaveLeaseLengthEnum,
            name="have_lease_length_enum",
            values_callable=enum_values,
        ),
        nullable=True,
    )

    encoded_answers: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), nullable=False, server_default="{}"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    smoke_vape: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    drink: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )

    user: Mapped["User"] = relationship("User", back_populates="survey", uselist=False)
