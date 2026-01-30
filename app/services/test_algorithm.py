import numpy as np
import time
import pandas as pd


synth_data = pd.read_csv("meteormate_synthetic_data")
synth_data.head()

cols_to_convert = ['housing_intent', "wake_time", "cleanliness", 'noise_tolerance', 'cooking_frequency', 'guest_frequency',
                   'roomate_closeness', 'on_campus_location', 'num_roomates', 'interests', 'honors', 'llc_interest'
                  ]
synth_data[cols_to_convert] = synth_data[cols_to_convert].apply(lambda x: x.astype('category').cat.codes)
synth_data.head()

filtered_synth_data = synth_data.drop(columns=['Unnamed: 0', 'have_lease_length', 'budget_min', 'budget_max', 'id', 'raw_move_in_date', 
                                               'has_date', 'move_in_date', 'have_lease'])
filtered_synth_data.head()

data = np.array(filtered_synth_data)
curr_user = np.expand_dims(data[0, :], axis=0)
other_users = data[1:, :]
print(curr_user.shape)
print(other_users.shape)

# Similarity matrix: shape (12, 20, 20)
# mat[q, i, j] = similarity between answer i and answer j for question q
# Diagonal is always 1.0. Unused slots (beyond a question's # of choices) are 0.
#
# Category codes are assigned alphabetically by pandas .cat.codes:
#
#  0  housing_intent : both(0) off_campus(1) on_campus(2)
#  1  wake_time      : early_bird(0) flexible(1) night_owl(2)
#  2  cleanliness    : neat_freak(0) relaxed(1) tidy(2)
#  3  noise_tolerance: loud(0) moderate(1) quiet(2)
#  4  cooking_freq   : never(0) often(1) rarely(2)
#  5  guest_freq     : never(0) often(1) sometimes(2)
#  6  roomate_close  : close_friends(0) friends(1) not_close(2)
#  7  on_campus_loc  : cc(0) freshman_dorms(1) northside(2) uv(3)
#  8  num_roomates   : no_preference(0) one(1) three(2) two(3)
#  9  interests      : Art(0) Cooking(1) Fashion(2) Fitness(3) Gaming(4)
#                      Hiking(5) Movies(6) Music(7) Photography(8) Reading(9)
#                      Social Media(10) Sports(11) Technology(12) Travel(13)
#                      Volunteering(14)
# 10  honors         : 0=no  1=yes
# 11  llc_interest   : 0=no  1=yes

NUM_QUESTIONS = 12
MAX_CHOICES = 20

sim = np.zeros((NUM_QUESTIONS, MAX_CHOICES, MAX_CHOICES))


def _place(q: int, block: list[list[float]]):
    """Write a small similarity block into the padded matrix."""
    n = len(block)
    sim[q, :n, :n] = np.array(block)


# ── Q0  housing_intent ──────────────────────────────────────────────
# both(0) is compatible with either direction
_place(0, [
    #  both  off   on
    [1.0,  0.5,  0.5],   # both
    [0.5,  1.0,  0.0],   # off_campus
    [0.5,  0.0,  1.0],   # on_campus
])

# ── Q1  wake_time ───────────────────────────────────────────────────
# ordinal: early_bird ← flexible → night_owl
_place(1, [
    #  early flex  night
    [1.0,  0.5,  0.0],   # early_bird
    [0.5,  1.0,  0.5],   # flexible
    [0.0,  0.5,  1.0],   # night_owl
])

# ── Q2  cleanliness ─────────────────────────────────────────────────
# natural scale: relaxed(1) < tidy(2) < neat_freak(0)
_place(2, [
    #  neat  relax tidy
    [1.0,  0.0,  0.5],   # neat_freak
    [0.0,  1.0,  0.5],   # relaxed
    [0.5,  0.5,  1.0],   # tidy
])

# ── Q3  noise_tolerance ─────────────────────────────────────────────
# ordinal: loud(0) ← moderate(1) ← quiet(2)
_place(3, [
    #  loud  mod   quiet
    [1.0,  0.4,  0.0],   # loud
    [0.4,  1.0,  0.4],   # moderate
    [0.0,  0.4,  1.0],   # quiet
])

# ── Q4  cooking_frequency ───────────────────────────────────────────
# natural scale: never(0) < rarely(2) < often(1)
# lower-stakes question, so similarities are generally higher
_place(4, [
    #  never often rarely
    [1.0,  0.3,  0.7],   # never
    [0.3,  1.0,  0.5],   # often
    [0.7,  0.5,  1.0],   # rarely
])

# ── Q5  guest_frequency ─────────────────────────────────────────────
# natural scale: never(0) < sometimes(2) < often(1)
# guests can be a major friction point
_place(5, [
    #  never often somet
    [1.0,  0.0,  0.3],   # never
    [0.0,  1.0,  0.5],   # often
    [0.3,  0.5,  1.0],   # sometimes
])

# ── Q6  roomate_closeness ───────────────────────────────────────────
# natural scale: not_close(2) < friends(1) < close_friends(0)
_place(6, [
    #  close frnd  notcl
    [1.0,  0.6,  0.1],   # close_friends
    [0.6,  1.0,  0.4],   # friends
    [0.1,  0.4,  1.0],   # not_close
])

# ── Q7  on_campus_location ──────────────────────────────────────────
# nominal — you either prefer the same area or you don't
_place(7, [
    #  cc   frsh  nrth  uv
    [1.0,  0.0,  0.0,  0.0],   # cc
    [0.0,  1.0,  0.0,  0.0],   # freshman_dorms
    [0.0,  0.0,  1.0,  0.0],   # northside
    [0.0,  0.0,  0.0,  1.0],   # uv
])

# ── Q8  num_roomates ────────────────────────────────────────────────
# no_preference(0) is flexible; natural count: one(1) < two(3) < three(2)
_place(8, [
    #  nopf  one  three two
    [1.0,  0.7,  0.7,  0.7],   # no_preference
    [0.7,  1.0,  0.1,  0.4],   # one
    [0.7,  0.1,  1.0,  0.6],   # three
    [0.7,  0.4,  0.6,  1.0],   # two
])

# ── Q9  interests ───────────────────────────────────────────────────
# 15 categories grouped by affinity:
#   Active   : Fitness(3), Hiking(5), Sports(11)
#   Creative : Art(0), Music(7), Photography(8), Fashion(2)
#   Indoor   : Gaming(4), Movies & TV(6), Reading(9), Technology(12)
#   Social   : Social Media(10), Volunteering(14), Travel(13)
#   Domestic : Cooking(1)
#
# same = 1.0 | same-group ≈ 0.3 | cross-group = 0.0

n_interests = 15
interest_sim = np.eye(n_interests)

groups = [
    [3, 5, 11],          # active
    [0, 2, 7, 8],        # creative
    [4, 6, 9, 12],       # indoor
    [10, 13, 14],        # social
]

for grp in groups:
    for a in grp:
        for b in grp:
            if a != b:
                interest_sim[a, b] = 0.3

sim[9, :n_interests, :n_interests] = interest_sim

# ── Q10 honors ──────────────────────────────────────────────────────
_place(10, [
    [1.0, 0.0],
    [0.0, 1.0],
])

# ── Q11 llc_interest ────────────────────────────────────────────────
_place(11, [
    [1.0, 0.0],
    [0.0, 1.0],
])

print("sim.shape:", sim.shape)
print("\nQ1 (wake_time):")
print(sim[1, :3, :3])
print("\nQ9 (interests, first 6×6):")
print(sim[9, :6, :6])

w = np.ones(shape=(1, 12))
sim = np.array(sim)
start_time = time.perf_counter()
question_idx = np.arange(12)
sim_scores = sim[question_idx, curr_user, other_users]
average_sim_scores = np.sum(w * sim_scores / np.sum(w, axis=-1), axis=1)
sorted_sim_indices = np.argsort(average_sim_scores)[::-1]
sorted_users = other_users[sorted_sim_indices]
average_sim_scores = np.expand_dims(average_sim_scores, axis=-1)[sorted_sim_indices]
end_time = time.perf_counter()

print(curr_user)
print(other_users[:5, :])
print(average_sim_scores)

print(f"Time: {end_time-start_time} seconds")


