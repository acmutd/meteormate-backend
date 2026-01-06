# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import logging
from typing import List, Dict

from sqlalchemy.orm import Session
from app.models.user import User
from app.models.survey import Survey
from app.models.matches import Match

logger = logging.getLogger("meteormate." + __name__)


class MatchingService:

    def __init__(self, db: Session):
        self.db = db

    async def find_potential_matches(self, user_id: str, limit: int = 10) -> List[Dict]:
        logger.info(f"Finding potential matches for User {user_id}")

        # get user's survey
        user_survey = self.db.query(Survey).filter(Survey.user_id == user_id).first()
        if not user_survey:
            logger.warning(f"User {user_id} has no survey, returning 0 matches")
            return []

        # get IDs of users already passed/matched
        interacted_user_ids = (
            self.db.query(Match.target_user_id).filter(Match.user_id == user_id).all()
        )
        # extract IDs
        seen_ids = {uid for (uid, ) in interacted_user_ids}
        seen_ids.add(user_id)  # exclude the user themselves obviously

        # get other users' surveys (excluding already matched/passed)
        other_surveys = (
            self.db.query(Survey).filter(Survey.user_id.notin_(seen_ids)).limit(limit * 2).all()
        )

        matches = []
        for survey in other_surveys:
            compatibility_score = self._calculate_compatibility(user_survey, survey)

            user = self.db.query(User).filter(User.id == survey.user_id).first()

            if not user:
                continue

            matches.append({
                "user": {
                    "uid": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "survey": {
                    "housing_type": survey.housing_type,
                    "budget_range": f"${survey.budget_min}-${survey.budget_max}",
                    "cleanliness_level": survey.cleanliness_level,
                    "noise_level": survey.noise_level,
                    "sleep_schedule": survey.sleep_schedule,
                    "interests": survey.interests
                },
                "compatibility_score": compatibility_score
            })

        # sort by compatibility score
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)

        logger.info(f"Found {len(matches)} potential matches for User {user_id}")
        return matches[:limit]

    def _calculate_compatibility(self, user_survey: Survey, other_survey: Survey) -> float:
        score = 0.0

        # budget compatibility (30% weight)
        if self._budgets_overlap(user_survey, other_survey):
            score += 30

        # lifestyle compatibility (40% weight)
        lifestyle_score = 0
        lifestyle_score += self._compare_numeric_preference(
            user_survey.cleanliness_level, other_survey.cleanliness_level, 2
        )
        lifestyle_score += self._compare_numeric_preference(
            user_survey.noise_level, other_survey.noise_level, 2
        )
        lifestyle_score += (10 if user_survey.sleep_schedule == other_survey.sleep_schedule else 0)
        lifestyle_score += (10 if user_survey.study_habits == other_survey.study_habits else 0)

        score += (lifestyle_score / 40) * 40

        # interests compatibility (20% weight)
        common_interests = set(user_survey.interests) & set(other_survey.interests)
        interest_score = min(len(common_interests) * 5, 20)
        score += interest_score

        # dealbreakers (-50 if any match)
        if self._has_deal_breaker_conflict(user_survey, other_survey):
            score -= 50

        return max(0, min(100, score))

    @staticmethod
    def _budgets_overlap(survey1: Survey, survey2: Survey) -> bool:
        return not (
            survey1.budget_max < survey2.budget_min or survey2.budget_max < survey1.budget_min
        )

    @staticmethod
    def _compare_numeric_preference(val1: int, val2: int, tolerance: int) -> float:
        diff = abs(val1 - val2)
        if diff <= tolerance:
            return 10 - (diff * 2)
        return 0

    @staticmethod
    def _has_deal_breaker_conflict(survey1: Survey, survey2: Survey) -> bool:
        # todo - implement deal breaker logic
        return False

    async def like_user(self, user_id: str, target_user_id: str) -> Dict:
        # todo - implementation for liking a user
        return {"status": "liked"}

    async def pass_user(self, user_id: str, target_user_id: str) -> Dict:
        # todo - implementation for passing a user
        return {"status": "passed"}

    async def get_mutual_matches(self, user_id: str) -> List[Dict]:
        # todo - implementation for getting mutual matches
        return []
