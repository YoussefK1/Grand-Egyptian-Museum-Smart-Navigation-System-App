"""
Build the GEM datasets:
  data/zones.csv, data/edges.csv          - museum navigation graph
  data/artifacts.csv                      - artifact catalogue (one row per object)
  data/questionnaire.json                 - tour-customisation questions
  data/DATA_SOURCES.md                    - provenance report
Run:  python scripts/build_dataset.py
"""
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from gemcore.constants import (CROWD, DEPTHS, ERAS, INTERESTS, MOBILITY, PACES, TIME_OPTIONS,  # noqa: E402
                               VISITOR_TYPES)
from gemcore.layout import FLOOR_LABELS, layout_as_tables  # noqa: E402
from artifact_seed import SEED  # noqa: E402

DATA = os.path.join(ROOT, "data")


def build():
    os.makedirs(DATA, exist_ok=True)
    zrows, erows = layout_as_tables()
    zones = pd.DataFrame(zrows)
    zones["floor_label"] = zones["floor"].map(FLOOR_LABELS)
    zones.to_csv(os.path.join(DATA, "zones.csv"), index=False)
    pd.DataFrame(erows).to_csv(os.path.join(DATA, "edges.csv"), index=False)

    zmap = zones.set_index("id")
    rows = []
    for i, rec in enumerate(SEED, start=1):
        (name, zone, era, period, cat, mat, tags, pop, mins, kid, desc, tier) = rec
        assert zone in zmap.index, f"unknown zone {zone} for {name}"
        z = zmap.loc[zone]
        rows.append(dict(
            artifact_id=f"A{i:03d}", name=name, zone_id=zone, gallery=z["name"], floor=int(z["floor"]),
            era_id=era, period=period, category=cat, material=mat, interest_tags=tags,
            popularity=pop, view_minutes=mins, kid_friendly=kid,
            crowd_level=round(min(1.0, pop / 10.0) ** 1.5, 2),
            step_free_access=1, description=desc,
            keywords=";".join(sorted(set(tags.split(";") + [cat.lower(), mat.lower().split()[0]]))),
            image_url="", image_file=f"data/images/A{i:03d}.jpg", source_tier=tier,
        ))
    art = pd.DataFrame(rows)
    # artifacts in the app prototype that have real image assets
    proto_img = {"Golden Burial Mask of Tutankhamun": "assets/images/tutankhamun_mask.png",
                 "Colossal Statue of Ramesses II": "assets/images/ramses_statue.png",
                 "Model of Funerary Boat of Ukhhotep": "assets/images/collection1.png",
                 "Statuette of a Falcon": "assets/images/collection3.png",
                 "Statue of the Scribe Mitri": "assets/images/collection5.png"}
    art["app_image_asset"] = art["name"].map(proto_img).fillna("")
    art.to_csv(os.path.join(DATA, "artifacts.csv"), index=False)

    q = {
        "version": 1,
        "questions": [
            {"id": "time_minutes", "type": "single", "title": "How much time do you have?",
             "options": [{"value": t, "label": f"{t // 60}h {t % 60:02d}m" if t % 60 else f"{t // 60}h"} for t in TIME_OPTIONS]},
            {"id": "eras", "type": "multi", "title": "Which periods of history attract you most?",
             "subtitle": "Pick as many as you like - or none for a balanced tour",
             "options": [{"value": e[0], "label": e[1], "hint": e[2]} for e in ERAS]},
            {"id": "interests", "type": "multi", "max": 5, "title": "What are your interests?",
             "subtitle": "Choose up to 5",
             "options": [{"value": i[0], "label": i[1], "icon": i[2]} for i in INTERESTS]},
            {"id": "visitor_type", "type": "single", "title": "Who is visiting?",
             "options": [{"value": v[0], "label": v[1]} for v in VISITOR_TYPES]},
            {"id": "pace", "type": "single", "title": "What is your visiting pace?",
             "options": [{"value": p[0], "label": p[1]} for p in PACES]},
            {"id": "depth", "type": "single", "title": "How deep do you want to go?",
             "options": [{"value": d[0], "label": d[1]} for d in DEPTHS]},
            {"id": "mobility", "type": "single", "title": "Any mobility needs?",
             "options": [{"value": m[0], "label": m[1]} for m in MOBILITY]},
            {"id": "crowd", "type": "single", "title": "How do you feel about crowds?",
             "options": [{"value": c[0], "label": c[1]} for c in CROWD]},
        ],
    }
    with open(os.path.join(DATA, "questionnaire.json"), "w", encoding="utf-8") as f:
        json.dump(q, f, indent=2, ensure_ascii=False)
    print(f"zones={len(zones)} edges={len(erows)} artifacts={len(art)}")
    print(art["source_tier"].value_counts().to_dict())
    print(art["era_id"].value_counts().to_dict())
    return art


if __name__ == "__main__":
    build()
