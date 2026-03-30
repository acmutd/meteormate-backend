# Created by Ryan Polasky | 7/12/25
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
        self.q_idx = np.arange(30)

    def find_potential_matches(self, user_id: str, limit: int = 10) -> List[str]:
        # get user's survey
        user_survey = self.db.query(Survey).filter(Survey.user_id == user_id).first()
        if not user_survey:
            return []

        # filter out all the inactive users
        other_surveys = self.db.query(Survey).join(User, Survey.user_id == User.id).filter(
            User.is_active == True,
            Survey.user_id != user_id
        ).all()
        other_profiles = self.db.query(UserProfile).join(User, UserProfile.user_id == User.id).filter(
            User.is_active == True,
            UserProfile.user_id != user_id
        ).all()

        other_ids = np.array([survey.user_id for survey in other_surveys], dtype=object)
        id_to_survey = {survey.user_id: survey for survey in other_surveys}
        id_to_profile = {profile.user_id: profile for profile in other_profiles}

        # parallelize compatibility calculations for all other users 
        user_vector = np.expand_dims(np.array(list(user_survey.relevant_answers)), axis=0) # shape = (1, Q) where Q is number of survey questions
        other_vectors = np.array([list(other_survey.relevant_answers) for other_survey in other_surveys]) # shape = (N, Q) where N is number of other users (that passed the inactivity filtering)
        sim_scores = self.sim_matrix[self.q_idx, user_vector, other_vectors] # shape = (Q, C, C) where C is max number of answer choices across any question (5 in our case, at least for now)
        average_sim_scores = np.sum(self.q_weights * sim_scores, axis=-1) / np.sum(self.q_weights) # shape = (N, 1)
        sorted_other_ids = other_ids[np.argsort(average_sim_scores)[::-1]] # shape = (N, 1)
    
        sorted_records = []
        for curr_id in list(sorted_other_ids):
            # get all the relevant database schema info for each user
            curr_user_survey_record = id_to_survey[curr_id]
            curr_user_profile_record = id_to_profile[curr_id]
            
            sorted_records.append({
                "user": {
                    "uid": curr_user_profile_record.user_id,
                    "first_name": curr_user_profile_record.first_name,
                    "last_name": curr_user_profile_record.last_name,
                    "gender": curr_user_profile_record.gender,
                    "major": curr_user_profile_record.major,
                    "classification": curr_user_profile_record.classification,
                    "bio": curr_user_profile_record.bio
                },
                # In the future, may only include a portion of the survey information
                "survey": {
                    "housing_intent": curr_user_survey_record.housing_intent,
                    "budget_min": curr_user_survey_record.budget_min,
                    "budget_max": curr_user_survey_record.budget_max,
                    "move_in_date": curr_user_survey_record.move_in_date,
                    "wake_time": curr_user_survey_record.wake_time,
                    "cleanliness": curr_user_survey_record.cleanliness,
                    "noise_tolerance": curr_user_survey_record.noise_tolerance,
                    "interests": curr_user_survey_record.interests,
                    "dealbreakers": curr_user_survey_record.dealbreakers,
                    "cooking_frequency": curr_user_survey_record.cooking_frequency,
                    "pet_preference": curr_user_survey_record.pet_preference,
                    "guests_frequency": curr_user_survey_record.guests_frequency,
                    "roommate_closeness": curr_user_survey_record.roommate_closeness,
                    "on_campus_locations": curr_user_survey_record.on_campus_locations,
                    "honors": curr_user_survey_record.honors,
                    "llc_interest": curr_user_survey_record.llc_interest,
                    "num_roommates": curr_user_survey_record.num_roommates,
                    "have_lease": curr_user_survey_record.have_lease,
                    "have_lease_length": curr_user_survey_record.have_lease_length,
                    "smoke_vape": curr_user_survey_record.smoke_vape,
                    "drink": curr_user_survey_record.drink
                }
            })
        
        return sorted_records[:limit]


    async def like_user(self, user_id: str, target_user_id: str) -> Dict:
        # todo - implementation for liking a user
        return {"status": "liked"}

    async def pass_user(self, user_id: str, target_user_id: str) -> Dict:
        # todo - implementation for passing a user
        return {"status": "passed"}

    async def get_mutual_matches(self, user_id: str) -> List[Dict]:
        # todo - implementation for getting mutual matches
        return []
