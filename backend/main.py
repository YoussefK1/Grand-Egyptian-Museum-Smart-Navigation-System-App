"""
GEM Smart Navigation API (FastAPI).

Run (from the project root):
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
Interactive docs: http://localhost:8000/docs
"""
from __future__ import annotations

import csv
import json
import os
import pickle
import sys
import time
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from gemcore.constants import ERAS, INTERESTS  # noqa: E402
from gemcore.features import normalise_visitor, pair_features  # noqa: E402
from gemcore.layout import FLOOR_LABELS  # noqa: E402
from gemcore.planner import TourPlanner  # noqa: E402

DATA, MODELS = os.path.join(ROOT, "data"), os.path.join(ROOT, "models")

app = FastAPI(title="GEM Smart Navigation API", version="1.0.0",
              description="Tour customisation (XGBoost), indoor navigation (graph routing) and AI artifact "
                          "collections (embeddings + K-Means/DBSCAN) for the Grand Egyptian Museum app.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

planner = TourPlanner()
graph = planner.graph
ART = planner.art.copy()
ART_BY_ID = {r["artifact_id"]: r for r in ART.to_dict("records")}
with open(os.path.join(DATA, "questionnaire.json"), encoding="utf-8") as f:
    QUESTIONNAIRE = json.load(f)
with open(os.path.join(MODELS, "artifact_clusters.json"), encoding="utf-8") as f:
    CLUSTERS = json.load(f)
CLUSTER_BY_ID = {c["cluster_id"]: c for c in CLUSTERS["clusters"]}
ART_CLUSTER = {p["artifact_id"]: p["cluster"] for p in CLUSTERS["points"]}
POINTS = {p["artifact_id"]: p for p in CLUSTERS["points"]}
with open(os.path.join(MODELS, "tour_ranker_meta.json")) as f:
    TOUR_META = json.load(f)
TEXT_MODEL = None
_pk = os.path.join(MODELS, "artifact_text_model.pkl")
if os.path.exists(_pk):
    with open(_pk, "rb") as f:
        TEXT_MODEL = pickle.load(f)
FEEDBACK_LOG = os.path.join(DATA, "feedback_log.csv")


def _clean(rec: dict) -> dict:
    out = {}
    for k, v in rec.items():
        if isinstance(v, (np.integer,)):
            v = int(v)
        elif isinstance(v, (np.floating,)):
            v = float(v)
        elif isinstance(v, float) and np.isnan(v):
            v = ""
        out[k] = v
    return out


def _artifact_public(a: dict) -> dict:
    a = _clean(a)
    cid = ART_CLUSTER.get(a["artifact_id"])
    return dict(
        artifact_id=a["artifact_id"], name=a["name"], description=a["description"], era_id=a["era_id"],
        era=dict((e[0], e[1]) for e in ERAS)[a["era_id"]], period=a["period"], category=a["category"],
        material=a["material"], interests=a["interest_tags"].split(";"), zone_id=a["zone_id"], gallery=a["gallery"],
        floor=a["floor"], floor_label=FLOOR_LABELS[a["floor"]], popularity=a["popularity"],
        view_minutes=a["view_minutes"], kid_friendly=a["kid_friendly"], image_asset=a.get("app_image_asset", ""),
        image_url=a.get("image_url", ""), source_tier=a["source_tier"],
        cluster_id=cid, cluster_label=CLUSTER_BY_ID[cid]["label"] if cid is not None else None,
    )


# ------------------------------------------------------------------ schemas
class TourRequest(BaseModel):
    time_minutes: int = Field(120, ge=30, le=600)
    eras: list[str] = []
    interests: list[str] = []
    visitor_type: str = "solo"
    pace: str = "balanced"
    depth: str = "balanced"
    mobility: str = "full"
    crowd: str = "neutral"
    start: str = "ENTRANCE"


class FeedbackIn(BaseModel):
    profile: TourRequest
    artifact_id: str
    rating: int = Field(..., ge=1, le=5, description="1 = not interested ... 5 = loved it")


class ClassifyIn(BaseModel):
    text: str = Field(..., min_length=3)


# ------------------------------------------------------------------ meta
@app.get("/health")
def health():
    return dict(status="ok", artifacts=len(ART), zones=len(graph.zones), time=time.time(),
                tour_model="XGBRanker", cluster_embedder=CLUSTERS["metrics"]["embedder"])


@app.get("/api/questionnaire")
def questionnaire():
    return QUESTIONNAIRE


@app.get("/api/model/info")
def model_info():
    return dict(tour_model=dict(metrics=TOUR_META["metrics"], label_source=TOUR_META["label_source"],
                                top_features=TOUR_META["feature_importance"]),
                clustering=CLUSTERS["metrics"])


# ------------------------------------------------------------------ 1) tour customisation
@app.post("/api/tour/recommend")
def recommend_tour(req: TourRequest):
    if req.start not in graph.zones:
        raise HTTPException(400, f"unknown start zone '{req.start}'")
    return planner.plan(req.model_dump())


# ------------------------------------------------------------------ 2) navigation
@app.get("/api/nav/zones")
def nav_zones(query: str = "", type: Optional[str] = None, floor: Optional[int] = None, limit: int = 60):
    zs = graph.search(query, limit=500) if query else list(graph.zones.values())
    if type:
        zs = [z for z in zs if z["type"] == type]
    if floor is not None:
        zs = [z for z in zs if int(z["floor"]) == floor]
    zs = [z for z in zs if z["type"] not in ("elevator", "stairs") or query]
    zs = sorted(zs, key=lambda z: (z["floor"], z["name"]))[:limit]
    return dict(floors={str(k): v for k, v in FLOOR_LABELS.items()},
                zones=[_clean({k: z[k] for k in ("id", "name", "type", "floor", "x", "y", "description",
                                                  "era_group", "theme")}) for z in zs])


@app.get("/api/nav/route")
def nav_route(start: str, goal: str,
              mode: str = Query("easiest", pattern="^(easiest|shortest|scenic|avoid_stairs|step_free)$")):
    try:
        return graph.route(start, goal, mode)
    except KeyError as exc:
        raise HTTPException(404, str(exc))


@app.get("/api/nav/nearest")
def nav_nearest(start: str, type: str, mode: str = "easiest"):
    z = graph.nearest(start, type, mode)
    if not z:
        raise HTTPException(404, "none found")
    return graph.route(start, z, mode)


@app.get("/api/nav/graph")
def nav_graph():
    """Full graph (zones + connections) so the app can draw floor plans and route offline."""
    zones = pd.read_csv(os.path.join(DATA, "zones.csv")).fillna("")
    edges = pd.read_csv(os.path.join(DATA, "edges.csv"))
    return dict(floors={str(k): v for k, v in FLOOR_LABELS.items()},
                zones=zones.to_dict("records"), edges=edges.to_dict("records"))


# ------------------------------------------------------------------ 3) AI collections
@app.get("/api/collections")
def collections():
    out = []
    for c in CLUSTERS["clusters"]:
        rep = ART_BY_ID[c["representative"]]
        out.append(dict(cluster_id=c["cluster_id"], label=c["label"], keywords=c["keywords"], size=c["size"],
                        dominant_era=c["dominant_era"], representative=c["representative"],
                        representative_name=rep["name"], image_asset=rep.get("app_image_asset", "") or ""))
    return dict(embedder=CLUSTERS["metrics"]["embedder"], k=CLUSTERS["metrics"]["kmeans_k"], collections=out)


@app.get("/api/collections/map")
def collections_map():
    return dict(points=CLUSTERS["points"],
                clusters=[dict(cluster_id=c["cluster_id"], label=c["label"]) for c in CLUSTERS["clusters"]])


@app.get("/api/collections/{cluster_id}")
def collection_detail(cluster_id: int):
    c = CLUSTER_BY_ID.get(cluster_id)
    if not c:
        raise HTTPException(404, "collection not found")
    return dict(cluster_id=cluster_id, label=c["label"], keywords=c["keywords"], size=c["size"],
                artifacts=[_artifact_public(ART_BY_ID[a]) for a in c["artifact_ids"]])


@app.post("/api/collections/classify")
def classify_text(body: ClassifyIn):
    """Assign a NEW artifact description to the closest thematic collection (text embedding)."""
    if TEXT_MODEL is None:
        raise HTTPException(501, "text model not available for the CLIP backend - use scripts/classify_with_clip.py")
    emb = TEXT_MODEL["embedder"].transform_text([body.text])[0]
    cen = TEXT_MODEL["centers"]
    sims = cen @ emb / (np.linalg.norm(cen, axis=1) + 1e-9)
    order = np.argsort(-sims)[:3]
    return dict(best=dict(cluster_id=int(order[0]), label=CLUSTER_BY_ID[int(order[0])]["label"],
                          score=round(float(sims[order[0]]), 3)),
                alternatives=[dict(cluster_id=int(i), label=CLUSTER_BY_ID[int(i)]["label"],
                                   score=round(float(sims[i]), 3)) for i in order[1:]])


# ------------------------------------------------------------------ artifacts
@app.get("/api/artifacts")
def artifacts(q: str = "", era: Optional[str] = None, interest: Optional[str] = None,
              cluster: Optional[int] = None, floor: Optional[int] = None, limit: int = 200):
    res = []
    ql = q.lower()
    for a in ART.to_dict("records"):
        if ql and ql not in (a["name"] + " " + a["description"] + " " + a["keywords"]).lower():
            continue
        if era and a["era_id"] != era:
            continue
        if interest and interest not in a["interest_tags"].split(";"):
            continue
        if cluster is not None and ART_CLUSTER.get(a["artifact_id"]) != cluster:
            continue
        if floor is not None and a["floor"] != floor:
            continue
        res.append(_artifact_public(a))
    res.sort(key=lambda a: -a["popularity"])
    return dict(count=len(res), artifacts=res[:limit])


@app.get("/api/artifacts/{artifact_id}")
def artifact_detail(artifact_id: str, from_zone: str = "ENTRANCE", mode: str = "easiest"):
    a = ART_BY_ID.get(artifact_id)
    if not a:
        raise HTTPException(404, "artifact not found")
    pub = _artifact_public(a)
    pub["how_to_get_there"] = graph.route(from_zone, a["zone_id"], mode) if from_zone in graph.zones else None
    pub["similar"] = [dict(_artifact_public(ART_BY_ID[n["artifact_id"]]), similarity=n["score"])
                      for n in CLUSTERS["neighbours"][artifact_id][:5]]
    return pub


@app.get("/api/artifacts/{artifact_id}/similar")
def similar(artifact_id: str, n: int = 6):
    if artifact_id not in CLUSTERS["neighbours"]:
        raise HTTPException(404, "artifact not found")
    return [dict(_artifact_public(ART_BY_ID[x["artifact_id"]]), similarity=x["score"])
            for x in CLUSTERS["neighbours"][artifact_id][:n]]


# ------------------------------------------------------------------ feedback loop (real labels for retraining)
@app.post("/api/feedback")
def feedback(fb: FeedbackIn):
    if fb.artifact_id not in ART_BY_ID:
        raise HTTPException(404, "artifact not found")
    new = not os.path.exists(FEEDBACK_LOG)
    with open(FEEDBACK_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "profile_json", "artifact_id", "rating"])
        w.writerow([int(time.time()), json.dumps(fb.profile.model_dump()), fb.artifact_id, fb.rating])
    return dict(status="stored", note="Run scripts/export_feedback.py then scripts/train_tour_model.py to retrain.")
