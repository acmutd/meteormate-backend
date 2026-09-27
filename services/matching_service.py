# Created by Ryan Polasky | 7/12/25
# Updated by Joel Guvireddy | 4/10/2026
# ACM MeteorMate | All Rights Reserved

import logging

import numpy as np
from sqlalchemy.orm import Session, selectinload

from models.matches import Match
from models.survey import HousingIntentEnum, OnCampusLocationEnum, PetPreferenceEnum
from models.user import User
from services.matching_config import NUM_QUESTIONS, q_weights, sim_matrix
from utils.matching import encode_answers

logger = logging.getLogger("meteormate." + __name__)


# in case user has old encoded values array, regenerate it
def _matching_answers(user: User) -> tuple[np.ndarray, bool]:
    answers = user.survey.encoded_answers
    regenerated = False

    if len(answers) != NUM_QUESTIONS:
        logger.info(
            "Regenerating %s matching answers for user %s",
            len(answers),
            user.id,
        )
        answers = encode_answers(user.survey, user)
        user.survey.encoded_answers = answers
        regenerated = True

    return np.asarray(answers), regenerated


def _requirements_accept(owner: User, other: User) -> bool:
    dealbreakers = owner.survey.dealbreakers

    if "smoke_vape" in dealbreakers and other.survey.smoke_vape:
        return False

    if "drink" in dealbreakers and other.survey.drink:
        return False

    if (
        "same_gender" in dealbreakers
        and owner.profile.gender != other.profile.gender
    ):
        return False

    return True


def _pets_are_compatible(a: User, b: User) -> bool:
    preferences = {a.survey.pet_preference, b.survey.pet_preference}

    if None in preferences:
        return False

    incompatible = {
        PetPreferenceEnum.NOT_OKAY,
        PetPreferenceEnum.HAVE_A_PET,
    }
    return not incompatible.issubset(preferences)


def _housing_modes(user: User) -> set[HousingIntentEnum]:
    intent = user.survey.housing_intent

    if intent == HousingIntentEnum.BOTH:
        return {HousingIntentEnum.ON_CAMPUS, HousingIntentEnum.OFF_CAMPUS}

    if intent in {HousingIntentEnum.ON_CAMPUS, HousingIntentEnum.OFF_CAMPUS}:
        return {intent}

    return set()


def _budgets_overlap(a: User, b: User) -> bool:
    a_min = a.survey.budget_min
    a_max = a.survey.budget_max
    b_min = b.survey.budget_min
    b_max = b.survey.budget_max

    if None in {a_min, a_max, b_min, b_max}:
        return False

    if a_min > a_max or b_min > b_max:
        return False

    return a_min <= b_max and b_min <= a_max


def _on_campus_locations_overlap(a: User, b: User) -> bool:
    shared_locations = set(a.survey.on_campus_locations) & set(
        b.survey.on_campus_locations
    )

    if (
        a.profile.classification != "freshman"
        or b.profile.classification != "freshman"
    ):
        shared_locations.discard(OnCampusLocationEnum.FRESHMAN_DORMS)

    return bool(shared_locations)


def _pair_meets_requirements(a: User, b: User) -> bool:
    if not _requirements_accept(a, b) or not _requirements_accept(b, a):
        return False

    if not _pets_are_compatible(a, b):
        return False

    if bool(a.survey.honors) != bool(b.survey.honors):
        return False

    shared_modes = _housing_modes(a) & _housing_modes(b)

    on_campus_works = (
        HousingIntentEnum.ON_CAMPUS in shared_modes
        and _on_campus_locations_overlap(a, b)
    )
    off_campus_works = (
        HousingIntentEnum.OFF_CAMPUS in shared_modes and _budgets_overlap(a, b)
    )

    return on_campus_works or off_campus_works


def top_k_matches(db: Session, user_id: str, k: int = 10) -> list[User]:
    current_user = (
        db.query(User)
        .options(selectinload(User.survey), selectinload(User.profile))
        .filter(User.id == user_id)
        .first()
    )
    if not current_user:
        logger.warning(f"User {user_id} attempted to find matches but does not exist")
        return []

    already_matched_subquery = (
        db.query(Match.target_user_id).filter(Match.user_id == user_id).subquery()
    )

    active_users = (
        db.query(User)
        .options(selectinload(User.survey), selectinload(User.profile))
        .filter(
            User.id != user_id,
            User.is_active.is_(True),
            User.id.notin_(already_matched_subquery),
            # make sure all candidates have completed survey and profile
            User.survey.has(),
            User.profile.has(),
        )
    )

    active_users = active_users.all()
    active_users = [
        candidate
        for candidate in active_users
        if _pair_meets_requirements(current_user, candidate)
    ]

    current_user_answers, answers_changed = _matching_answers(current_user)

    if len(active_users) == 0:
        if answers_changed:
            db.commit()
        logger.info(f"No potential matches found for user {user_id}")
        return []

    logger.info(
        f"User {user_id} has {len(active_users)} potential matches after hard requirement filtering"
    )

    uids = np.array([user.id for user in active_users], dtype=object)
    uid_to_user = {user.id: user for user in active_users}

    q_idx = np.arange(NUM_QUESTIONS)

    potential_match_answers = []
    for uid in uids:
        answers, regenerated = _matching_answers(uid_to_user[uid])
        potential_match_answers.append(answers)
        answers_changed = answers_changed or regenerated

    if answers_changed:
        db.commit()
        logger.info("Saved regenerated matching answers")

    potential_match_answers = np.array(potential_match_answers)
    sim_scores = sim_matrix[q_idx, current_user_answers, potential_match_answers] # (N, Q)
    avg_sim_scores = np.sum(q_weights * sim_scores, axis=-1) / np.sum(q_weights) # (N,) 
    sorted_uids = uids[avg_sim_scores.argsort()[::-1]]

    top_k_uids = sorted_uids[:k]
    top_k_matches = [uid_to_user[uid] for uid in top_k_uids]

    logger.info(f"Returning top {len(top_k_matches)} matches for user {user_id}")

    return top_k_matches
