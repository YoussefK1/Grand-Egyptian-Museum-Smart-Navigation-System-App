"""
Train the XGBoost learning-to-rank model that scores every artifact for a visitor profile.
Input : data/tour_training_data.csv.gz  (synthetic now; real feedback can be appended - see backend /feedback)
Output: models/tour_ranker.json, models/tour_ranker_meta.json (metrics + feature importance)
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import ndcg_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
DATA, MODELS = os.path.join(ROOT, "data"), os.path.join(ROOT, "models")
os.makedirs(MODELS, exist_ok=True)


def mean_ndcg(df, score_col, k):
    vals, p = [], []
    for _, g in df.groupby("visitor_id", sort=False):
        y = g["relevance"].to_numpy()[None, :]
        s = g[score_col].to_numpy()[None, :]
        vals.append(ndcg_score(y, s, k=k))
        top = np.argsort(-s[0])[:k]
        p.append((y[0][top] >= 2).mean())
    return float(np.mean(vals)), float(np.mean(p))


def main():
    df = pd.read_csv(os.path.join(DATA, "tour_training_data.csv.gz"))
    extra = os.path.join(DATA, "real_feedback_training.csv")
    if os.path.exists(extra):                       # optional: real labelled rows from the app
        df = pd.concat([df, pd.read_csv(extra)], ignore_index=True)
    vids = df["visitor_id"].unique()
    rng = np.random.default_rng(0)
    rng.shuffle(vids)
    n = len(vids)
    tr, va, te = set(vids[: int(.7 * n)]), set(vids[int(.7 * n): int(.85 * n)]), set(vids[int(.85 * n):])
    feats = [c for c in df.columns if c not in ("visitor_id", "artifact_id", "relevance")]
    parts = {k: df[df["visitor_id"].isin(s)].sort_values("visitor_id", kind="stable") for k, s in
             (("train", tr), ("val", va), ("test", te))}

    model = xgb.XGBRanker(objective="rank:ndcg", n_estimators=600, learning_rate=0.06, max_depth=6,
                          subsample=0.85, colsample_bytree=0.85, min_child_weight=3, tree_method="hist",
                          eval_metric="ndcg@10", early_stopping_rounds=40, random_state=7)
    model.fit(parts["train"][feats], parts["train"]["relevance"], qid=parts["train"]["visitor_id"],
              eval_set=[(parts["val"][feats], parts["val"]["relevance"])], eval_qid=[parts["val"]["visitor_id"]],
              verbose=False)

    test = parts["test"].copy()
    test["xgb"] = model.predict(test[feats])
    test["pop"] = test["a_pop"]
    test["rule"] = test["x_era_match"] * 2.4 + test["x_overlap_ratio"] * 1.9      # hand-written content baseline
    test["rand"] = rng.random(len(test))
    metrics = {}
    for name in ("xgb", "rule", "pop", "rand"):
        for k in (5, 10, 20):
            nd, pr = mean_ndcg(test, name, k)
            metrics[f"{name}_ndcg@{k}"] = round(nd, 4)
            metrics[f"{name}_precision@{k}"] = round(pr, 4)
    imp = dict(sorted(zip(feats, map(float, model.feature_importances_)), key=lambda t: -t[1]))
    meta = dict(features=feats, best_iteration=int(model.best_iteration),
                n_train_visitors=len(tr), n_val_visitors=len(va), n_test_visitors=len(te),
                label_source="synthetic simulator (scripts/simulate_visitors.py) + optional real feedback",
                metrics=metrics, feature_importance={k: round(v, 4) for k, v in list(imp.items())[:25]})
    model.save_model(os.path.join(MODELS, "tour_ranker.json"))
    with open(os.path.join(MODELS, "tour_ranker_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(metrics, indent=1))
    print("top features:", list(imp)[:8])


if __name__ == "__main__":
    main()
