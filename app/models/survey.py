# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Survey(Base):  # todo - make these relevant to whatever we end up asking in our survey
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))

    # roommate preferences
    housing_type = Column(String)  # 'dorm', 'apartment', 'house'
    budget_min = Column(Integer)
    budget_max = Column(Integer)
    move_in_date = Column(DateTime)
    lease_length = Column(String)  # 'semester', 'year', 'summer'

    # lifestyle preferences
    cleanliness_level = Column(Integer)  # 1-5 scale
    noise_level = Column(Integer)  # 1-5 scale
    guests_frequency = Column(String)  # 'never', 'rarely', 'sometimes', 'often'
    study_habits = Column(String)  # 'library', 'room', 'common_areas'
    sleep_schedule = Column(String)  # 'early_bird', 'night_owl', 'flexible'

    # interests/compatibility
    interests = Column(JSON)
    personality_traits = Column(JSON)
    deal_breakers = Column(JSON)  # smoking, pets, etc

    # ai processing
    ai_summary = Column(Text)
    compatibility_vector = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="survey")
