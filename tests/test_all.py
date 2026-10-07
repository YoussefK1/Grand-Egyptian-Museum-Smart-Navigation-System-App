import os
import sys
import warnings

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
warnings.filterwarnings("ignore")

from gemcore.constants import ERA_IDS, INTEREST_IDS  # noqa: E402
from gemcore.navigation import MuseumGraph  # noqa: E402
from gemcore.planner import TourPlanner  # noqa: E402


@pytest.fixture(scope="module")
def graph():
    return MuseumGraph()


@pytest.fixture(scope="module")
def planner():
    return TourPlanner()


# ---------------------------------------------------------------- dataset integrity
def test_artifact_dataset_is_valid():
    art = pd.read_csv(os.path.join(ROOT, "data", "artifacts.csv"))
    zones = set(pd.read_csv(os.path.join(ROOT, "data", "zones.csv"))["id"])
    assert len(art) >= 100
    assert art["artifact_id"].is_unique and art["name"].is_unique
    assert set(art["zone_id"]) <= zones
    assert set(art["era_id"]) <= set(ERA_IDS)
    for tags in art["interest_tags"]:
        assert set(tags.split(";")) <= set(INTEREST_IDS)
    assert art["description"].str.len().min() > 40
    assert art["source_tier"].isin(["confirmed_web", "prototype_app", "representative"]).all()


# ---------------------------------------------------------------- navigation
def test_graph_is_connected(graph):
    dist, _ = graph._dijkstra("ENTRANCE", "shortest", 0.0)
    assert set(dist) == set(graph.zones)


def test_step_free_graph_reaches_everything_without_stairs(graph):
    dist, _ = graph._dijkstra("ENTRANCE", "step_free", 0.0)
    assert set(dist) == set(graph.zones)
    for z in ("G12", "TUT_4", "CAVE_2", "GS_TOP"):
        assert graph.route("ENTRANCE", z, "step_free")["uses_stairs"] is False


def test_route_structure_and_symmetry(graph):
    r = graph.route("ENTRANCE", "G12", "easiest")
    assert r["found"] and r["steps"][0]["kind"] == "start" and r["steps"][-1]["kind"] == "arrive"
    assert r["nodes"][0]["id"] == "ENTRANCE" and r["nodes"][-1]["id"] == "G12"
    back = graph.route("G12", "ENTRANCE", "easiest")
    assert abs(back["distance_m"] - r["distance_m"]) < 1.0


def test_scenic_mode_uses_grand_staircase(graph):
    assert graph.route("GRAND_HALL", "GS_TOP", "scenic")["uses_stairs"] is True


def test_unknown_zone_raises(graph):
    with pytest.raises(KeyError):
        graph.route("ENTRANCE", "NOPE")


# ---------------------------------------------------------------- tour planner
PROFILES = [
    dict(time_minutes=60, pace="fast", depth="highlights"),
    dict(time_minutes=120, eras=["tutankhamun"], interests=["gold_jewelry", "royalty"], visitor_type="couple"),
    dict(time_minutes=180, interests=["animals"], visitor_type="family_kids", pace="relaxed"),
    dict(time_minutes=240, eras=["middle_kingdom"], interests=["writing_literature"], depth="deep"),
    dict(time_minutes=90, eras=["new_kingdom"], interests=["mummies_afterlife"], mobility="wheelchair"),
]


@pytest.mark.parametrize("profile", PROFILES)
def test_tour_respects_time_budget(planner, profile):
    plan = planner.plan(profile)
    assert plan["n_stops"] >= 1 and plan["n_artifacts"] >= 1
    assert plan["total_minutes"] <= profile["time_minutes"] + 1e-6
    ids = [a["artifact_id"] for s in plan["stops"] for a in s["artifacts"]]
    assert len(ids) == len(set(ids))


def test_wheelchair_tour_never_uses_stairs(planner):
    plan = planner.plan(PROFILES[-1])
    assert not any(s["leg"]["uses_stairs"] for s in plan["stops"])


def test_interests_change_the_tour(planner):
    gold = planner.plan(dict(time_minutes=120, interests=["gold_jewelry"]))
    boats = planner.plan(dict(time_minutes=120, interests=["ships_transport"]))
    g = {a["artifact_id"] for s in gold["stops"] for a in s["artifacts"]}
    b = {a["artifact_id"] for s in boats["stops"] for a in s["artifacts"]}
    assert g != b
    art = planner.art.set_index("artifact_id")
    gold_share = sum("gold_jewelry" in art.loc[i, "interest_tags"] for i in g) / len(g)
    assert gold_share >= 0.4


def test_era_preference_is_respected(planner):
    plan = planner.plan(dict(time_minutes=120, eras=["late_greco_roman"]))
    art = planner.art.set_index("artifact_id")
    share = sum(art.loc[a["artifact_id"], "era_id"] == "late_greco_roman" for s in plan["stops"] for a in s["artifacts"])
    assert share / plan["n_artifacts"] >= 0.5


def test_more_time_gives_more_content(planner):
    short = planner.plan(dict(time_minutes=60))
    long_ = planner.plan(dict(time_minutes=240))
    assert long_["n_artifacts"] > short["n_artifacts"]


def test_start_location_is_respected(planner):
    plan = planner.plan(dict(time_minutes=90, start="G09"))
    assert plan["stops"][0]["leg"]["nodes"][0]["id"] == "G09"


# ---------------------------------------------------------------- API
def test_api_end_to_end():
    from fastapi.testclient import TestClient
    from backend.main import app
    c = TestClient(app)
    assert c.get("/health").json()["status"] == "ok"
    assert len(c.get("/api/questionnaire").json()["questions"]) == 8
    r = c.post("/api/tour/recommend", json=dict(time_minutes=90, interests=["royalty"]))
    assert r.status_code == 200 and r.json()["n_stops"] >= 1
    assert c.post("/api/tour/recommend", json=dict(start="NOPE")).status_code == 400
    r = c.get("/api/nav/route", params=dict(start="ENTRANCE", goal="TUT_4", mode="step_free"))
    assert r.status_code == 200 and r.json()["found"]
    assert c.get("/api/nav/route", params=dict(start="ENTRANCE", goal="XXX")).status_code == 404
    cols = c.get("/api/collections").json()
    assert cols["k"] == len(cols["collections"]) >= 6
    d = c.get(f"/api/collections/{cols['collections'][0]['cluster_id']}").json()
    assert d["artifacts"]
    assert c.get("/api/artifacts/A002").json()["similar"]
    assert c.get("/api/collections/map").json()["points"]
