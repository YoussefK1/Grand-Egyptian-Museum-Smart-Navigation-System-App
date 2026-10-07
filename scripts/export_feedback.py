"""Convert data/feedback_log.csv (ratings collected by the app) into extra training rows for the ranker."""
import json, os, sys
import pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from gemcore.features import artifact_matrix, normalise_visitor, pair_features  # noqa

log = os.path.join(ROOT, "data", "feedback_log.csv")
if not os.path.exists(log):
    sys.exit("no feedback yet")
art = pd.read_csv(os.path.join(ROOT, "data", "artifacts.csv"))
amat = artifact_matrix(art)
fb = pd.read_csv(log)
rows = []
for n, (pj, aid, rating) in enumerate(zip(fb["profile_json"], fb["artifact_id"], fb["rating"])):
    v = normalise_visitor(json.loads(pj))
    X = pair_features(v, art, amat)
    X.insert(0, "visitor_id", 1_000_000 + n)       # one query group per feedback item
    X.insert(1, "artifact_id", art["artifact_id"].to_numpy())
    X["relevance"] = 0
    X.loc[art["artifact_id"] == aid, "relevance"] = {1: 0, 2: 1, 3: 1, 4: 2, 5: 3}[int(rating)]
    rows.append(X[X["artifact_id"] == aid])
out = pd.concat(rows)
out.to_csv(os.path.join(ROOT, "data", "real_feedback_training.csv"), index=False)
print("exported", len(out), "labelled rows")
