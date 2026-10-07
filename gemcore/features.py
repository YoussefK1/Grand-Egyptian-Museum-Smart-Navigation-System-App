"""Feature engineering shared by training (scripts/) and inference (backend/)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .constants import ERA_IDS, INTEREST_IDS, VISITOR_TYPES

PACE_ORD = {"relaxed": 0, "balanced": 1, "fast": 2}
DEPTH_ORD = {"highlights": 0, "balanced": 1, "deep": 2}
MOB_ORD = {"full": 0, "avoid_stairs": 1, "wheelchair": 2}
VTYPES = [v[0] for v in VISITOR_TYPES]

CATEGORIES = ["Amulet", "Archive", "Architecture", "Boat", "Boat part", "Chariot", "Coffin", "Cosmetics", "Deposit",
              "Display", "Figurine", "Funerary", "Furniture", "Game", "Instrument", "Inscription", "Jewelry", "Mask",
              "Model", "Monument", "Mummy", "Papyrus", "Portrait", "Pottery", "Reconstruction", "Regalia", "Relief",
              "Sarcophagus", "Seal", "Shabti", "Shrine", "Statue", "Statuette", "Stela", "Tablet", "Textile", "Tool",
              "Vessel", "Viewpoint", "Weapon"]
CAT_IDX = {c: i for i, c in enumerate(CATEGORIES)}


def normalise_visitor(v: dict) -> dict:
    """Fill defaults and validate a visitor profile coming from the app."""
    out = dict(
        time_minutes=int(v.get("time_minutes", 120)),
        eras=[e for e in v.get("eras", []) if e in ERA_IDS],
        interests=[i for i in v.get("interests", []) if i in INTEREST_IDS][:5],
        visitor_type=v.get("visitor_type", "solo") if v.get("visitor_type") in VTYPES else "solo",
        pace=v.get("pace", "balanced") if v.get("pace") in PACE_ORD else "balanced",
        depth=v.get("depth", "balanced") if v.get("depth") in DEPTH_ORD else "balanced",
        mobility=v.get("mobility", "full") if v.get("mobility") in MOB_ORD else "full",
        crowd=v.get("crowd", "neutral") if v.get("crowd") in ("avoid", "neutral") else "neutral",
        start=v.get("start", "ENTRANCE"),
    )
    out["time_minutes"] = int(min(max(out["time_minutes"], 30), 600))
    return out


def visitor_vector(v: dict) -> dict:
    f = {
        "v_time": v["time_minutes"],
        "v_pace": PACE_ORD[v["pace"]],
        "v_depth": DEPTH_ORD[v["depth"]],
        "v_mobility": MOB_ORD[v["mobility"]],
        "v_crowd_avoid": int(v["crowd"] == "avoid"),
        "v_n_eras": len(v["eras"]),
        "v_n_interests": len(v["interests"]),
    }
    for t in VTYPES:
        f[f"v_type_{t}"] = int(v["visitor_type"] == t)
    for e in ERA_IDS:
        f[f"v_era_{e}"] = int(e in v["eras"])
    for i in INTEREST_IDS:
        f[f"v_int_{i}"] = int(i in v["interests"])
    return f


def artifact_matrix(art: pd.DataFrame) -> pd.DataFrame:
    """Static per-artifact features (computed once)."""
    m = pd.DataFrame({
        "a_era": art["era_id"].map({e: i for i, e in enumerate(ERA_IDS)}).astype(int),
        "a_pop": art["popularity"].astype(float),
        "a_view": art["view_minutes"].astype(float),
        "a_kid": art["kid_friendly"].astype(float),
        "a_crowd": art["crowd_level"].astype(float),
        "a_floor": art["floor"].astype(int),
        "a_cat": art["category"].map(CAT_IDX).fillna(-1).astype(int),
    })
    tags = art["interest_tags"].str.split(";")
    for i in INTEREST_IDS:
        m[f"a_tag_{i}"] = tags.apply(lambda t, i=i: int(i in t))
    return m


def pair_features(v: dict, art: pd.DataFrame, amat: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per artifact for a single visitor (visitor + artifact + interaction features)."""
    amat = amat if amat is not None else artifact_matrix(art)
    n = len(amat)
    vf = visitor_vector(v)
    X = amat.copy()
    for k, val in vf.items():
        X[k] = val
    eras = set(v["eras"])
    tags = art["interest_tags"].str.split(";")
    ints = set(v["interests"])
    overlap = tags.apply(lambda t: len(ints.intersection(t))).to_numpy()
    X["x_era_match"] = art["era_id"].apply(lambda e: (1.0 if e in eras else 0.0) if eras else 0.5).to_numpy()
    X["x_overlap"] = overlap
    X["x_overlap_ratio"] = overlap / len(ints) if ints else np.full(n, 0.5)
    X["x_kid_family"] = art["kid_friendly"].to_numpy() * vf["v_type_family_kids"]
    X["x_pop_highlights"] = art["popularity"].to_numpy() * (v["depth"] == "highlights")
    X["x_pop_deep"] = art["popularity"].to_numpy() * (v["depth"] == "deep")
    X["x_stairs_flag"] = (art["floor"].between(1, 3)).astype(int).to_numpy() * (vf["v_mobility"] > 0)
    X["x_crowd_avoid"] = art["crowd_level"].to_numpy() * vf["v_crowd_avoid"]
    return X


FEATURE_ORDER: list[str] | None = None


def feature_columns(art: pd.DataFrame) -> list[str]:
    v = normalise_visitor({})
    return list(pair_features(v, art).columns)
