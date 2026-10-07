"""
Generate a SYNTHETIC visitor-preference dataset used to train the XGBoost tour ranker.

Why synthetic?  No logged visitor data exists for the GEM app yet. We therefore simulate visitors whose
answers to the questionnaire (time, era, interests, ...) drive a hidden "enjoyment" utility for each
artifact, plus personal noise and a hidden per-category taste the model cannot see. The grade (0-3) is the
simulated relevance label. When real users start rating tour stops, the backend's /feedback endpoint
stores real labels so the same training script can be re-run on real data.

Outputs:
  data/visitor_profiles.csv       - one row per simulated visitor (questionnaire answers)
  data/tour_training_data.csv     - one row per (visitor, artifact) pair with features + relevance grade
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from gemcore.constants import ERA_IDS, INTEREST_IDS, PACES, DEPTHS, MOBILITY, TIME_OPTIONS, VISITOR_TYPES  # noqa
from gemcore.features import artifact_matrix, normalise_visitor, pair_features  # noqa

DATA = os.path.join(ROOT, "data")
RNG = np.random.default_rng(42)

TYPE_INTEREST_BIAS = {
    "family_kids": ["animals", "ships_transport", "war_weapons", "gold_jewelry"],
    "student": ["writing_literature", "discovery_archaeology", "architecture", "religion_gods"],
    "couple": ["gold_jewelry", "art_statues", "royalty", "daily_life"],
    "solo": INTEREST_IDS,
    "group": ["royalty", "mummies_afterlife", "architecture", "gold_jewelry"],
}


def sample_visitor():
    vt = RNG.choice([v[0] for v in VISITOR_TYPES], p=[0.28, 0.22, 0.2, 0.12, 0.18])
    n_era = RNG.choice([0, 1, 2, 3], p=[0.15, 0.4, 0.3, 0.15])
    eras = list(RNG.choice(ERA_IDS, size=n_era, replace=False)) if n_era else []
    n_int = int(RNG.choice([1, 2, 3, 4, 5], p=[0.1, 0.25, 0.3, 0.2, 0.15]))
    pool = TYPE_INTEREST_BIAS[vt]
    probs = np.array([3.0 if i in pool and vt != "solo" else 1.0 for i in INTEREST_IDS])
    interests = list(RNG.choice(INTEREST_IDS, size=n_int, replace=False, p=probs / probs.sum()))
    return normalise_visitor(dict(
        time_minutes=int(RNG.choice(TIME_OPTIONS, p=[0.12, 0.15, 0.28, 0.25, 0.14, 0.06])),
        eras=eras, interests=interests, visitor_type=vt,
        pace=RNG.choice([p[0] for p in PACES], p=[0.3, 0.5, 0.2]),
        depth=RNG.choice([d[0] for d in DEPTHS], p=[0.35, 0.45, 0.2]),
        mobility=RNG.choice([m[0] for m in MOBILITY], p=[0.85, 0.08, 0.07]),
        crowd=RNG.choice(["avoid", "neutral"], p=[0.4, 0.6]),
    ))


def utility(v, art, X):
    eras = set(v["eras"])
    era_m = X["x_era_match"].to_numpy()
    ov = X["x_overlap_ratio"].to_numpy()
    pop = art["popularity"].to_numpy()
    kid = art["kid_friendly"].to_numpy()
    tags = art["interest_tags"].str.split(";")
    u = -1.0 + 2.4 * era_m + 1.9 * ov
    pop_w = {"highlights": 0.22, "balanced": 0.08, "deep": -0.12}[v["depth"]] * (1.3 if v["pace"] == "fast" else 1.0)
    u += pop_w * (pop - 5)
    if v["visitor_type"] == "family_kids":
        u += 1.2 * (kid - 0.6)
    if v["visitor_type"] == "student":
        u += 0.4 * tags.apply(lambda t: int(("writing_literature" in t) or ("discovery_archaeology" in t))).to_numpy()
    floors = art["floor"].to_numpy()
    if v["mobility"] == "wheelchair":
        u -= 0.5 * ((floors >= 1) & (floors <= 3))
    elif v["mobility"] == "avoid_stairs":
        u -= 0.2 * ((floors >= 1) & (floors <= 3))
    if v["crowd"] == "avoid":
        u -= 0.9 * art["crowd_level"].to_numpy()
    # hidden personal taste per category + idiosyncratic noise (unobservable by the model)
    cats = art["category"].unique()
    taste = {c: RNG.normal(0, 0.35) for c in cats}
    u += art["category"].map(taste).to_numpy() + RNG.normal(0, 0.45, len(art))
    return u


def grade(u):
    return np.digitize(u, [0.9, 1.7, 2.6])


def main(n_visitors=3000):
    art = pd.read_csv(os.path.join(DATA, "artifacts.csv"))
    amat = artifact_matrix(art)
    profiles, frames = [], []
    for vid in range(n_visitors):
        v = sample_visitor()
        X = pair_features(v, art, amat)
        g = grade(utility(v, art, X))
        X.insert(0, "visitor_id", vid)
        X.insert(1, "artifact_id", art["artifact_id"].to_numpy())
        X["relevance"] = g
        frames.append(X)
        profiles.append(dict(visitor_id=vid, time_minutes=v["time_minutes"], eras=";".join(v["eras"]),
                             interests=";".join(v["interests"]), visitor_type=v["visitor_type"], pace=v["pace"],
                             depth=v["depth"], mobility=v["mobility"], crowd=v["crowd"]))
    pd.DataFrame(profiles).to_csv(os.path.join(DATA, "visitor_profiles.csv"), index=False)
    train = pd.concat(frames, ignore_index=True)
    train.to_csv(os.path.join(DATA, "tour_training_data.csv.gz"), index=False, compression="gzip")
    print("visitors", n_visitors, "rows", len(train))
    print(train["relevance"].value_counts(normalize=True).sort_index().round(3).to_dict())


if __name__ == "__main__":
    main()
