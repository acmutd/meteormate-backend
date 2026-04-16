# Created by Ryan Polasky | 7/12/25
# Updated by Joel Guvireddy with help from Atharva Mishra | 4/10/2026
# ACM MeteorMate | All Rights Reserved

import logging
import numpy as np
from typing import List, Dict

from sqlalchemy.orm import Session
from models.user import User
from models.user_profile import UserProfile
from models.survey import Survey
from models.matches import Match

logger = logging.getLogger("meteormate." + __name__)

GENDER_INDEX = {
    "female": 0,
    "male": 1,
    "non_binary": 2,
    "prefer_not_to_say": 3,
    "other": 4,
}

CATEGORY_INDEX = {
    "STEM & Engineering": 0,
    "Business & Management": 1,
    "Life Sciences & Health": 2,
    "Humanities & Arts": 3,
    "Social Sciences & Policy": 4,
}

CLASSIFICATION_INDEX = {
    "freshman": 0,
    "sophomore": 1,
    "junior": 2,
    "senior": 3,
    "graduate": 4,
}

HOUSING_INTENT_INDEX = {
    "both": 0,
    "off_campus": 1,
    "on_campus": 2,
}

WAKE_TIME_INDEX = {
    "early_bird": 0,
    "flexible": 1,
    "night_owl": 2,
}

CLEANLINESS_INDEX = {
    "neat_freak": 0,
    "relaxed": 1,
    "tidy": 2,
}

NOISE_TOLERANCE_INDEX = {
    "loud": 0,
    "moderate": 1,
    "quiet": 2,
}

COOKING_FREQUENCY_INDEX = {
    "never": 0,
    "rarely": 1,
    "often": 2,
}

PET_PREFERENCE_INDEX = {
    "okay": 0,
    "not_okay": 1,
    "have_a_pet": 2,
}

GUESTS_FREQUENCY_INDEX = {
    "never": 0,
    "sometimes": 1,
    "often": 2,
}

ROOMMATE_CLOSENESS_INDEX = {
    "not_close": 0,
    "friends": 1,
    "close_friends": 2,
}

ON_CAMPUS_LOCATION_INDEX = {
    "cc": 0,
    "freshman_dorms": 1,
    "northside": 2,
    "uv": 3,
}

NUM_ROOMMATES_INDEX = {
    "no_preference": 0,
    "one": 1,
    "two": 2,
    "three": 3,
}

def get_major_category(self, major: str) -> int:
    major_categories = {
        "STEM & Engineering": [
            "biomedical-engineering",
            "computer-engineering",
            "computer-science",
            "data-science",
            "electrical-engineering",
            "mechanical-engineering",
            "software-engineering",
            "actuarial-science",
            "chemistry",
            "geosciences",
            "mathematics",
            "physics",
        ],
        "Business & Management": [
            "accounting",
            "business-administration",
            "business-analytics",
            "finance",
            "global-business",
            "healthcare-management",
            "human-resource-management",
            "information-technology-systems",
            "marketing",
            "supply-chain-management",
        ],
        "Life Sciences & Health": [
            "biochemistry",
            "biology",
            "molecular-biology",
            "neuroscience",
            "child-learning-development",
            "cognitive-science",
            "psychology",
            "speech-language-hearing",
        ],
        "Humanities & Arts": [
            "animation-games",
            "arts-technology-emerging-communication",
            "art-history",
            "history",
            "interdisciplinary-studies",
            "literature",
            "philosophy",
            "visual-performing-arts",
        ],
        "Social Sciences & Policy": [
            "criminology-criminal-justice",
            "economics",
            "geospatial-information-sciences",
            "international-political-economy",
            "political-science",
            "public-affairs",
            "public-policy",
            "sociology",
        ],
    }

    for category, majors in major_categories.items():
        if major in majors:
            return CATEGORY_INDEX[category]
    
    return -1

class MatchingService:
    def __init__(self, db, sim_matrix: np.array, question_weights: np.array):
        self.db = db
        self.sim_matrix = sim_matrix
        self.q_weights = question_weights
        self.q_idx = np.arange(31)
        self.exclude_fields = {"dealbreakers", "user", "user_id"}

    def get_answers_array(self, survey: Survey, profile: UserProfile):
        answers = [
            GENDER_INDEX.get(profile.gender, -1),
            get_major_category(profile.major),
            CLASSIFICATION_INDEX.get(profile.classification, -1),
            HOUSING_INTENT_INDEX.get(survey.housing_intent, -1),
            WAKE_TIME_INDEX.get(survey.wake_time, -1),
            CLEANLINESS_INDEX.get(survey.cleanliness, -1),
            NOISE_TOLERANCE_INDEX.get(survey.noise_tolerance, -1),
            COOKING_FREQUENCY_INDEX.get(survey.cooking_frequency, -1),
            PET_PREFERENCE_INDEX.get(survey.pet_preference, -1),
            GUESTS_FREQUENCY_INDEX.get(survey.guests_frequency, -1),
            ROOMMATE_CLOSENESS_INDEX.get(survey.roommate_closeness, -1),
            ON_CAMPUS_LOCATION_INDEX.get(profile.on_campus_location, -1),
            1 if survey.honors else 0,
            1 if survey.llc_interest else 0,
            NUM_ROOMMATES_INDEX.get(survey.num_roommates, -1),
        ]
        
        # for interest in survey.interests:
        #     answers.append(interest)
        
        # answers.append(1 if survey.honors else 0)
        # answers.append(1 if survey.llc_interest else 0)
        # answers.append(NUM_ROOMMATES_INDEX.get(survey.num_roommates, -1))
        
        return answers

    def find_potential_matches(self, user_id: str, limit: int = 10) -> List[User]:
        # current user's survey
        current_user = self.db.query(User).filter(User.id == user_id).first()
        if not current_user:
            logger.warning(
                f"User {user_id} attempted to find matches but does not exist"
            )
            return []

        current_user_answers = np.array(
            self.get_answers_array(current_user.survey, current_user.profile)
        )

        # get user's survey and profile of active users
        active_users = (
            self.db.query(User).filter(User.id != user_id, User.is_active == True).all()
        )

        uids = np.array([user.user_id for user in active_users], dtype=object)
        uid_to_user = {user.user_id: user for user in active_users}

        uid_scores = {}

        for uid in uids:
            potential_match = uid_to_user[uid]

            if (
                "smoke_vape" in current_user.survey.dealbreakers
                and potential_match.survey.smoke_vape
            ):
                continue
            if (
                "drink" in current_user.survey.dealbreakers
                and potential_match.survey.drink
            ):
                continue
            if (
                "same_gender" in current_user.survey.dealbreakers
                and potential_match.profile.gender == current_user.profile.gender
            ):
                continue

            potential_match_answers = np.array(
                self.get_answers_array(potential_match.survey, potential_match.profile)
            )
            sim_scores = self.sim_matrix[
                self.q_idx, current_user_answers, potential_match_answers
            ]
            average_sim_score = np.sum(self.q_weights * sim_scores) / np.sum(
                self.q_weights
            )
            uid_scores[uid] = average_sim_score

        # Sort uid to users by similarity score and return top N
        sorted_uids = sorted(uid_scores, key=uid_scores.get, reverse=True)
        top_k_uids = sorted_uids[:limit]
        top_k_matches = [uid_to_user[uid] for uid in top_k_uids]

        return top_k_matches

    async def like_user(self, user_id: str, target_user_id: str) -> Dict:
        # todo - implementation for liking a user
        return {"status": "liked"}

    async def pass_user(self, user_id: str, target_user_id: str) -> Dict:
        # todo - implementation for passing a user
        return {"status": "passed"}

    async def get_mutual_matches(self, user_id: str) -> List[Dict]:
        # todo - implementation for getting mutual matches
        return []
