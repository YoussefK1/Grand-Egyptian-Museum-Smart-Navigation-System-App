"""
AI exhibition module: embed every artifact (CLIP text+image, or TF-IDF fallback), cluster the embeddings
into thematic groups with K-Means (final grouping) and DBSCAN (outlier / 'unique masterpiece' detection),
then write models/artifact_clusters.json + docs/figures/artifact_clusters.png.

  python scripts/build_clusters.py                 # auto backend (CLIP if available)
  python scripts/build_clusters.py --backend clip  # force CLIP (needs: pip install torch transformers pillow)
  python scripts/build_clusters.py --backend tfidf
"""
import argparse
import json
import os
import pickle
import sys
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
from sklearn.metrics import (adjusted_rand_score, davies_bouldin_score, normalized_mutual_info_score,
                             silhouette_score)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from gemcore.constants import ERAS, INTERESTS  # noqa: E402
from gemcore.embeddings import STOP, artifact_text, get_embedder  # noqa: E402

DATA, MODELS = os.path.join(ROOT, "data"), os.path.join(ROOT, "models")
ERA_NAME = {e[0]: e[1] for e in ERAS}
INT_NAME = {i[0]: i[1] for i in INTERESTS}


def choose_k(E, k_range=range(8, 13)):
    scores = {}
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=20, random_state=0).fit(E)
        scores[k] = silhouette_score(E, km.labels_, metric="cosine")
    return max(scores, key=scores.get), scores


def tune_dbscan(E):
    best = None
    for eps in np.arange(0.25, 0.95, 0.025):
        for ms in (2, 3, 4):
            lab = DBSCAN(eps=eps, min_samples=ms, metric="cosine").fit_predict(E)
            n_cl = len(set(lab)) - (1 if -1 in lab else 0)
            noise = (lab == -1).mean()
            if n_cl < 3 or noise > 0.25:
                continue
            mask = lab != -1
            if len(set(lab[mask])) < 2:
                continue
            s = silhouette_score(E[mask], lab[mask], metric="cosine") - 0.5 * noise
            if best is None or s > best[0]:
                best = (s, eps, ms, lab)
    return best


def label_cluster(df_c, E_terms, vec):
    """Human readable label: dominant theme(s) + dominant object type (+ era when the cluster is era-pure)."""
    era = Counter(df_c["era_id"]).most_common(1)[0]
    tags = Counter(t for ts in df_c["interest_tags"] for t in ts.split(";"))
    cats = Counter(df_c["category"]).most_common(2)
    top_tags = [t for t, _ in tags.most_common(2)]
    terms = np.asarray(E_terms.mean(axis=0)).ravel()
    names = vec.get_feature_names_out()
    words = [names[i] for i in terms.argsort()[::-1][:8] if " " not in names[i]][:5]
    main = " & ".join(INT_NAME[t].split(" & ")[0] for t in top_tags)
    purity = era[1] / len(df_c)
    suffix = f" - {ERA_NAME[era[0]].split(' (')[0].split(' & ')[0]}" if purity >= 0.6 else ""
    return f"{main}{suffix}", words, cats


def main(backend="auto"):
    art = pd.read_csv(os.path.join(DATA, "artifacts.csv"))
    emb = get_embedder(backend)
    E = emb.fit_transform(art)
    print("embedder:", emb.name, E.shape)

    k, sil = choose_k(E)
    km = KMeans(n_clusters=k, n_init=30, random_state=0).fit(E)
    labels = km.labels_
    db = tune_dbscan(E)
    db_labels = db[3] if db else np.full(len(art), -1)

    vec = TfidfVectorizer(stop_words=STOP, ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    T = vec.fit_transform([artifact_text(r) for _, r in art.iterrows()])

    # 2-D map for the app (t-SNE on cosine geometry; PCA init for stability)
    pca2 = PCA(n_components=2, random_state=0).fit_transform(E)
    tsne = TSNE(n_components=2, perplexity=12, metric="cosine", init="pca", random_state=0).fit_transform(E)
    xy = (tsne - tsne.min(0)) / (tsne.max(0) - tsne.min(0))

    clusters = []
    sims = E @ km.cluster_centers_.T / (np.linalg.norm(km.cluster_centers_, axis=1)[None, :] + 1e-9)
    for c in range(k):
        idx = np.where(labels == c)[0]
        sub = art.iloc[idx]
        name, words, cats = label_cluster(sub, T[idx], vec)
        order = idx[np.argsort(-sims[idx, c])]
        clusters.append(dict(
            cluster_id=int(c), label=name, keywords=words, top_categories=[c_[0] for c_ in cats],
            size=int(len(idx)), representative=art.iloc[order[0]]["artifact_id"],
            dominant_era=Counter(sub["era_id"]).most_common(1)[0][0],
            artifact_ids=[art.iloc[i]["artifact_id"] for i in order],
        ))
    # make labels unique
    seen = Counter()
    for c in clusters:
        seen[c["label"]] += 1
        if seen[c["label"]] > 1:
            c["label"] += f" ({c['top_categories'][0]}s)"

    pts = []
    for i, r in art.iterrows():
        pts.append(dict(artifact_id=r["artifact_id"], name=r["name"], cluster=int(labels[i]),
                        x=round(float(xy[i, 0]), 4), y=round(float(xy[i, 1]), 4),
                        outlier=bool(db_labels[i] == -1), density_group=int(db_labels[i])))

    # similarity lists (top-6 neighbours) for "similar artifacts"
    S = E @ E.T
    np.fill_diagonal(S, -1)
    neigh = {art.iloc[i]["artifact_id"]: [dict(artifact_id=art.iloc[j]["artifact_id"], score=round(float(S[i, j]), 3))
                                          for j in np.argsort(-S[i])[:6]] for i in range(len(art))}

    metrics = dict(
        embedder=emb.name, n_artifacts=int(len(art)), embedding_dim=int(E.shape[1]),
        kmeans_k=int(k), silhouette_by_k={int(a): round(float(b), 4) for a, b in sil.items()},
        kmeans_silhouette=round(float(silhouette_score(E, labels, metric="cosine")), 4),
        kmeans_davies_bouldin=round(float(davies_bouldin_score(E, labels)), 4),
        kmeans_vs_era_NMI=round(float(normalized_mutual_info_score(art["era_id"], labels)), 4),
        kmeans_vs_category_NMI=round(float(normalized_mutual_info_score(art["category"], labels)), 4),
        kmeans_vs_gallery_ARI=round(float(adjusted_rand_score(art["zone_id"], labels)), 4),
        dbscan=(dict(eps=round(float(db[1]), 3), min_samples=int(db[2]),
                     n_clusters=int(len(set(db_labels)) - (1 if -1 in db_labels else 0)),
                     noise_points=int((db_labels == -1).sum())) if db else None),
        note="K-Means gives the thematic groups shown in the app; DBSCAN marks 'unique pieces' (noise) that "
             "do not belong to a dense theme.")
    out = dict(metrics=metrics, clusters=clusters, points=pts, neighbours=neigh)
    with open(os.path.join(MODELS, "artifact_clusters.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    # a text model so new artifacts can be assigned to a cluster at runtime (tfidf backend only)
    if emb.name.startswith("tfidf"):
        with open(os.path.join(MODELS, "artifact_text_model.pkl"), "wb") as f:
            pickle.dump(dict(embedder=emb, centers=km.cluster_centers_), f)
    print(json.dumps(metrics, indent=1))
    for c in clusters:
        print(f"[{c['cluster_id']:>2}] {c['label']:<45} n={c['size']:<3} {c['keywords'][:4]}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        os.makedirs(os.path.join(ROOT, "docs", "figures"), exist_ok=True)
        fig, ax = plt.subplots(1, 2, figsize=(15, 6))
        ax[0].scatter(xy[:, 0], xy[:, 1], c=labels, cmap="tab20", s=45)
        ax[0].set_title(f"K-Means (k={k}) - {emb.name}")
        ax[1].scatter(xy[:, 0], xy[:, 1], c=db_labels, cmap="tab20", s=45)
        o = db_labels == -1
        ax[1].scatter(xy[o, 0], xy[o, 1], c="black", marker="x", s=40, label="DBSCAN noise")
        ax[1].legend()
        ax[1].set_title("DBSCAN (cosine) - density groups & outliers")
        plt.tight_layout()
        plt.savefig(os.path.join(ROOT, "docs", "figures", "artifact_clusters.png"), dpi=130)
    except Exception as exc:
        print("plot skipped:", exc)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="auto", choices=["auto", "clip", "tfidf"])
    main(ap.parse_args().backend)
