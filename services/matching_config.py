import numpy as np


NUM_QUESTIONS = 30
MAX_NUM_ANSWER_CHOICES = 5

sim_matrix = np.zeros((NUM_QUESTIONS, MAX_NUM_ANSWER_CHOICES, MAX_NUM_ANSWER_CHOICES))
q_weights = np.ones((1, NUM_QUESTIONS)) # for now, all questions are weighted equally

def _place(q: int, block: list[list[float]]):
    n = len(block)
    sim_matrix[q, :n, :n] = np.array(block)

# For each question's matrix q_mat, q_mat[i][j] represents how similar choosing answer is to choosing answer j

# gender 
_place(0, [
    [1.00,  0.50,  0.50,  0.50,  0.50],  # Female
    [0.50,  1.00,  0.50,  0.50,  0.50],  # Male
    [0.50,  0.50,  1.00,  0.50,  0.50],  # Non-binary
    [0.50,  0.50,  0.50,  1.00,  0.50],  # Prefer not to say
    [0.50,  0.50,  0.50,  0.50,  1.00],  # Other
])

# major (majors are grouped into 5 categories)
_place(1, [
    [1.00,  0.30,  0.40,  0.10,  0.15],  # STEM & Engineering
    [0.30,  1.00,  0.20,  0.15,  0.35],  # Business & Management
    [0.40,  0.20,  1.00,  0.10,  0.30],  # Life Sciences & Health
    [0.10,  0.15,  0.10,  1.00,  0.45],  # Humanities & Arts
    [0.15,  0.35,  0.30,  0.45,  1.00],  # Social Sciences & Policy
])

# classification 
_place(2, [
    [1.00,  0.80,  0.50,  0.30,  0.10],  # Freshman
    [0.80,  1.00,  0.80,  0.50,  0.20],  # Sophomore
    [0.50,  0.80,  1.00,  0.80,  0.30],  # Junior
    [0.30,  0.50,  0.80,  1.00,  0.50],  # Senior
    [0.10,  0.20,  0.30,  0.50,  1.00],  # Graduate
])

# housing intent
_place(3, [
    #  both  off   on
    [1.0,  0.5,  0.5],   # both
    [0.5,  1.0,  0.0],   # off_campus
    [0.5,  0.0,  1.0],   # on_campus
])

# wake time (3 answer choices)
_place(4, [
    [1.0,  0.5,  0.0],   # early_bird
    [0.5,  1.0,  0.5],   # flexible
    [0.0,  0.5,  1.0],   # night_owl
])

# cleanliness
_place(5, [
    [1.0,  0.3,  0.5],   # neat_freak
    [0.2,  1.0,  0.5],   # relaxed
    [0.5,  0.3,  1.0],   # tidy
])

# noise_tolerance
_place(6, [
    [1.0,  0.7,  0.5],   # loud
    [0.4,  1.0,  0.8],   # moderate
    [0.1,  0.7,  1.0],   # quiet
])

# cooking_frequency
_place(7, [
    [1.0,  0.5,  0.7],   # never   — fine with another non-cook, also fine with a cook
    [0.5,  1.0,  0.7],   # often   — enjoys cooking, slightly prefers someone similar
    [0.7,  0.7,  1.0],   # rarely  — flexible, gets along with both
])

# pet_preference
_place(8, [
    [1.0, 0.9, 0.8],  # okay with pet
    [0.7, 1.0, 0.0],  # not okay with pet
    [0.7, 0.0, 0.5],   # has a pet (two people having pets may cause problems, which is why last value is 0.5 and not 1)
])

# guest_frequency
_place(9, [
    [1.0,  0.05, 0.35],  # never     — strong clash with "often"
    [0.05, 1.0,  0.60],  # often     — somewhat compatible with "sometimes"
    [0.35, 0.60, 1.0],   # sometimes — middle ground
])

# roommate_closeness
_place(10, [
    [1.0,  0.6,  0.05],  # close_friends
    [0.6,  1.0,  0.40],  # friends
    [0.05, 0.40, 1.0],   # not_close
])

# on_campus_location 
_place(11, [
    [1.0,  0.0,  0.0,  0.3],   # cc
    [0.0,  1.0,  0.0,  0.0],   # freshman_dorms - no compatibility with other locations since freshman are required to stay in freshman dorms
    [0.0,  0.0,  1.0,  0.0],   # northside
    [0.3,  0.0,  0.0,  1.0],   # uv
])

# interests
for i in range(12, 28):
    _place(i, [
        [1.0, 0.5], # has interest
        [0.5, 0.5]  # doesn't have interest
    ])


# ── Q10 honors ──────────────────────────────────────────────────────
_place(28, [
    [1.0, 0.5],
    [0.5, 1.0],
])

# ── Q11 llc_interest ────────────────────────────────────────────────
_place(29, [
    [1.0, 0.5],
    [0.5, 1.0],
])

# num_roommates
_place(30, [
    [1.0,  0.8,  0.80, 0.80],   # no_preference
    [0.8,  1.0,  0.35, 0.1],  # one
    [0.8,  0.6, 1.0, 0.4],   # two
    [0.8,  0.4, 0.60, 1.0],  # three
])