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


class MatchingService:
    def __init__(self, db, sim_matrix: np.array, question_weights: np.array):
        self.db = db
        self.sim_matrix = sim_matrix
        self.q_weights = question_weights
        self.q_idx = np.arange(31)
        self.exclude_fields = {"dealbreakers", "user", "user_id"}

    def get_answers_array(self, survey: Survey):
        return [
            getattr(survey, col.name)
            for col in survey.__table__.columns
            if col.name not in self.exclude_fields
        ]
        
    def find_potential_matches(self, user_id: str, limit: int = 10) -> List[User]:
        # current user's survey
        current_user = self.db.query(User).filter(User.id == user_id).first()
        if not current_user:
            logger.warning(f"User {user_id} attempted to find matches but does not exist")
            return []
        
        current_user_answers = np.array(self.get_answers_array(current_user.survey))
        
        # get user's survey and profile of active users
        active_users = self.db.query(User).filter(
            User.id != user_id,
            User.is_active == True
        ).all()
        
        uids = np.array([user.user_id for user in active_users], dtype=object)
        uid_to_user = {user.user_id: user for user in active_users}
        
        uid_scores = {}
        
        for uid in uids:
            potential_match = uid_to_user[uid]
            
            if "smoke_vape" in current_user.survey.dealbreakers and potential_match.survey.smoke_vape:
                continue
            if "drink" in current_user.survey.dealbreakers and potential_match.survey.drink:
                continue
            if "same_gender" in current_user.survey.dealbreakers and potential_match.profile.gender == current_user.profile.gender:
                continue
            
            potential_match_answers = np.array(self.get_answers_array(potential_match.survey))
            sim_scores = self.sim_matrix[self.q_idx, current_user_answers, potential_match_answers]
            average_sim_score = np.sum(self.q_weights * sim_scores) / np.sum(self.q_weights)
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
