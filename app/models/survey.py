# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import Enum as PGEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class HousingTypeEnum(str, enum.Enum):
    DORM = "dorm"
    APARTMENT = "apartment"
    HOUSE = "house"


class LeaseLengthEnum(str, enum.Enum):
    SEMESTER = "semester"
    YEAR = "year"
    SUMMER = "summer"
    OTHER = "other"


class GuestsFrequencyEnum(str, enum.Enum):
    NEVER = "never"
    RARELY = "rarely"
    SOMETIMES = "sometimes"
    OFTEN = "often"


class StudyHabitsEnum(str, enum.Enum):
    LIBRARY = "library"
    ROOM = "room"
    COMMON_AREAS = "common_areas"
    ANYWHERE = "anywhere"


class SleepScheduleEnum(str, enum.Enum):
    EARLY_BIRD = "early_bird"
    NIGHT_OWL = "night_owl"
    FLEXIBLE = "flexible"


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Text, ForeignKey("users.id"))

    # roommate preferences
    housing_types = Column(
        ARRAY(PGEnum(HousingTypeEnum, name="housingtypeenum")), nullable=False, server_default="{}"
    )
    budget_min = Column(Integer)
    budget_max = Column(Integer)
    move_in_date = Column(DateTime)
    housing_types = Column(
        ARRAY(PGEnum(HousingTypeEnum, name="leaselengthenum")), nullable=False, server_default="{}"
    )

    # lifestyle preferences
    cleanliness_level = Column(Integer)  # 1-5 scale
    noise_level = Column(Integer)  # 1-5 scale
    guest_frequency = Column(
        ARRAY(PGEnum(HousingTypeEnum, name="guestfrequencyenum")),
        nullable=False,
        server_default="{}"
    )
    study_habits = Column(
        ARRAY(PGEnum(HousingTypeEnum, name="studyhabitsenum")), nullable=False, server_default="{}"
    )
    sleep_schedule = Column(PGEnum(SleepScheduleEnum))

    # interests/compatibility
    interests = Column(JSONB)
    personality_traits = Column(JSONB)
    deal_breakers = Column(JSONB)  # smoking, pets, etc

    # ai processing
    ai_summary = Column(Text)
    compatibility_vector = Column(JSON)
    tags = Column(JSONB)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="survey")
