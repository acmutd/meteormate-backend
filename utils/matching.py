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

POSSIBLE_INTERESTS = [
    "Climbing",
    "Anime",
    "Running",
    "Instruments",
    "Reading",
    "Gaming",
    "Travel",
    "Blogging",
    "Movies",
    "Singing",
    "Shopping",
    "Cooking",
    "Art",
    "Organized",
    "Photos",
    "Basketball",
    "Music",
    "EDM",
    "Coding",
    "Bollywood",
    "Sleeping",
    "Scrapbook",
    "Legos",
    "D&D",
    "Soccer",
    "Pickleball",
    "Chess",
    "Concerts",
    "K-Pop",
    "Dancing",
    "Languages",
    "Badminton",
]

def encode_answers(survey: Survey) -> list[int]:
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
    ]
    
    for interest in POSSIBLE_INTERESTS:
        answers.append(1 if interest in survey.interests else 0)
    
    answers.append(1 if survey.honors else 0)
    answers.append(1 if survey.llc_interest else 0)
    answers.append(NUM_ROOMMATES_INDEX.get(survey.num_roommates, -1))

    return answers