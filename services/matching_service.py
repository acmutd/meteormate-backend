# Created by Ryan Polasky | 7/12/25
# Updated by Joel Guvireddy | 4/10/2026
# ACM MeteorMate | All Rights Reserved

import logging
import numpy as np
from typing import List, Dict

from sqlalchemy.orm import Session
from models.user import User
from models.user_profile import UserProfile
from models.survey import Survey
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
            User.is_active == True,
            User.id.notin_(already_matched_subquery),
        ).all()
    )

    if len(active_users) == 0:
        logger.info(f"No potential matches found for user {user_id}")
        return []

    logger.info(
        f"User {user_id} has {len(active_users)} potential matches after filtering out inactive users and already matched users"
    )

    uids = np.array([user.user_id for user in active_users], dtype=object)
    uid_to_user = {user.user_id: user for user in active_users}

    uid_scores = {}

    q_idx = np.arange(47)

    for uid in uids:
        potential_match = uid_to_user[uid]
        
        if not potential_match.survey or not potential_match.profile:
            logger.warning(f"Potential match {uid} for user {user_id} is missing survey or profile data, skipping")
            continue

        if ("smoke_vape" in current_user.survey.dealbreakers and potential_match.survey.smoke_vape):
            continue
        if ("drink" in current_user.survey.dealbreakers and potential_match.survey.drink):
            continue
        if (
            "same_gender" in current_user.survey.dealbreakers
            and potential_match.profile.gender != current_user.profile.gender
        ):
            continue

        potential_match_answers = np.array(potential_match.survey.encoded_answers)
        sim_scores = sim_matrix[q_idx, current_user_answers, potential_match_answers]
        average_sim_score = np.sum(q_weights * sim_scores) / np.sum(q_weights)
        uid_scores[uid] = average_sim_score

    sorted_uids = sorted(uid_scores, key=uid_scores.get, reverse=True)

    logger.info(
        f"User has {len(sorted_uids)} matches after applying dealbreaker filters and calculating similarity scores"
    )

    top_k_uids = sorted_uids[:k]
    top_k_matches = [uid_to_user[uid] for uid in top_k_uids]

    logger.info(f"Returning top {len(top_k_matches)} matches for user {user_id}")

    return top_k_matches
