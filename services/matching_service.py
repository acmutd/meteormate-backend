# Created by Ryan Polasky | 7/12/25
# Updated by Joel Guvireddy | 4/10/2026
# ACM MeteorMate | All Rights Reserved

import logging
from typing import List

import numpy as np

from sqlalchemy.orm import Session
from models.user import User
from models.matches import Match
from services.matching_config import sim_matrix, q_weights

logger = logging.getLogger("meteormate." + __name__)


def top_k_matches(db: Session, user_id: str, k: int = 10) -> List[User]:
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        logger.warning(f"User {user_id} attempted to find matches but does not exist")
        return []

    current_user_answers = np.array(current_user.survey.encoded_answers)

    already_matched_subquery = (
        db.query(Match.target_user_id).filter(Match.user_id == user_id).subquery()
    )

    active_users = (
        db.query(User).filter(
            User.id != user_id,
            User.is_active.is_(True),
            User.id.notin_(already_matched_subquery),
            # make sure all candidates have completed survey and profile
            User.survey.has(), 
            User.profile.has()
        )
    )

    # filter out users violating dealbreakers
    if "smoke_vape" in current_user.survey.dealbreakers:
        active_users = active_users.filter(User.survey.has(Survey.smoke_vape == False))
    
    if "drink" in current_user.survey.dealbreakers:
        active_users = active_users.filter(User.survey.has(Survey.drink == False))
    
    if "same_gender" in current_user.survey.dealbreakers:
        active_users = active_users.filter(User.profile.has(UserProfile.gender == current_user.profile.gender))
        
    if "freshman_dorms" in current_user.survey.on_campus_locations:
        active_users = active_users.filter(User.survey.has(Survey.on_campus_locations.any("freshman_dorms")))

    active_users = active_users.all()

    if len(active_users) == 0:
        logger.info(f"No potential matches found for user {user_id}")
        return []

    logger.info(
        f"User {user_id} has {len(active_users)} potential matches after filtering out inactive users, already matched users, and users violating dealbreakers"
    )

    uids = np.array([user.id for user in active_users], dtype=object)
    uid_to_user = {user.id: user for user in active_users}

    uid_scores = {}

    q_idx = np.arange(47)

    potential_match_answers = np.array([uid_to_user[uid].survey.encoded_answers for uid in uids])
    sim_scores = sim_matrix[q_idx, current_user_answers, potential_match_answers] # (N, Q)
    avg_sim_scores = np.sum(q_weights * sim_scores, axis=-1) / np.sum(q_weights) # (N,) 
    sorted_uids = uids[avg_sim_scores.argsort()[::-1]]

    top_k_uids = sorted_uids[:k]
    top_k_matches = [uid_to_user[uid] for uid in top_k_uids]

    logger.info(f"Returning top {len(top_k_matches)} matches for user {user_id}")

    return top_k_matches
