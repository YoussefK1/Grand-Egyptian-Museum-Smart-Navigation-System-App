"""Export the JSON bundles the Flutter app ships with, so it also works with NO server (demo / offline mode):
   nav_graph.json, questionnaire.json, collections.json, demo_tours.json  ->  gem_app/assets/data/"""
import json, os, sys
import pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from gemcore.planner import TourPlanner  # noqa
from gemcore.layout import FLOOR_LABELS  # noqa
from gemcore.constants import ERAS  # noqa

OUT = os.path.join(ROOT, "gem_app", "assets", "data")
os.makedirs(OUT, exist_ok=True)
D = os.path.join(ROOT, "data")
z = pd.read_csv(f"{D}/zones.csv").fillna("")
e = pd.read_csv(f"{D}/edges.csv")
json.dump(dict(floors={str(k): v for k, v in FLOOR_LABELS.items()}, zones=z.to_dict("records"), edges=e.to_dict("records")),
          open(f"{OUT}/nav_graph.json", "w"))
json.dump(json.load(open(f"{D}/questionnaire.json")), open(f"{OUT}/questionnaire.json", "w"))

cl = json.load(open(f"{ROOT}/models/artifact_clusters.json", encoding="utf-8"))
art = pd.read_csv(f"{D}/artifacts.csv").fillna({"app_image_asset": "", "image_url": ""})
byid = {r["artifact_id"]: r for r in art.to_dict("records")}
era = {x[0]: x[1] for x in ERAS}
cid = {p["artifact_id"]: p["cluster"] for p in cl["points"]}
def pub(a):
    r = byid[a]
    return dict(artifact_id=a, name=r["name"], description=r["description"], era=era[r["era_id"]], period=r["period"],
                category=r["category"], material=r["material"], zone_id=r["zone_id"], gallery=r["gallery"],
                floor=int(r["floor"]), popularity=int(r["popularity"]), view_minutes=float(r["view_minutes"]),
                image_asset=r["app_image_asset"], cluster_id=cid[a])
cols, det = [], {}
for c in cl["clusters"]:
    rep = byid[c["representative"]]
    cols.append(dict(cluster_id=c["cluster_id"], label=c["label"], keywords=c["keywords"], size=c["size"],
                     dominant_era=c["dominant_era"], representative_name=rep["name"], image_asset=rep["app_image_asset"]))
    det[str(c["cluster_id"])] = dict(cluster_id=c["cluster_id"], label=c["label"], keywords=c["keywords"], size=c["size"],
                                     artifacts=[pub(a) for a in c["artifact_ids"]])
json.dump(dict(metrics=cl["metrics"], collections=cols, details=det, points=cl["points"],
               clusters=[dict(cluster_id=c["cluster_id"], label=c["label"]) for c in cl["clusters"]]),
          open(f"{OUT}/collections.json", "w", encoding="utf-8"), ensure_ascii=False)

P = TourPlanner()
presets = [
    ("Highlights in 1 hour", dict(time_minutes=60, pace="fast", depth="highlights")),
    ("Tutankhamun & gold, 2 hours", dict(time_minutes=120, eras=["tutankhamun"], interests=["gold_jewelry", "royalty"])),
    ("Family adventure, 3 hours", dict(time_minutes=180, interests=["animals", "ships_transport"], visitor_type="family_kids", pace="relaxed")),
    ("Pyramid builders & writing, 3 hours", dict(time_minutes=180, eras=["old_kingdom", "middle_kingdom"], interests=["writing_literature", "architecture"])),
    ("Mummies & afterlife (step-free), 90 min", dict(time_minutes=90, interests=["mummies_afterlife", "religion_gods"], mobility="wheelchair")),
    ("Full day deep dive, 5 hours", dict(time_minutes=300, depth="deep", pace="relaxed")),
]
demo = [dict(name=n, profile=p, plan=P.plan(p)) for n, p in presets]
json.dump(demo, open(f"{OUT}/demo_tours.json", "w"))
print("exported", os.listdir(OUT))
