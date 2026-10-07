# GEM Smart Navigation System - technical report (draft for your submission)

## 1. Problem
Visitors to the Grand Egyptian Museum face a very large site (12 main galleries, Tutankhamun galleries, Grand Staircase, boats museum).
The system provides (1) a personalised tour, (2) indoor routing and (3) AI-organised artifact collections in one mobile app.

## 2. Architecture
Flutter app <-> FastAPI (`backend/main.py`) <-> `gemcore` (planner, navigation, features) + trained models.
The app has on-device fallbacks (offline router, bundled collections, demo tours).

## 3. Dataset (see data/DATA_SOURCES.md)
126 artifacts, 50 zones, 72 links, 8-question questionnaire, 3,000 synthetic visitors (378k labelled pairs). Provenance tiers are explicit.

## 4. Module 1 - tour customisation (XGBoost)
* **Features** (57): visitor (time, pace, depth, mobility, crowd, visitor type, 6 era flags, 12 interest flags), artifact (era, popularity,
  viewing time, kid-friendliness, crowd, floor, category, 12 tags) and interaction features (era match, interest overlap, family x kid, popularity x depth, stairs, crowd).
* **Model:** `XGBRanker`, objective `rank:ndcg`, one query group per visitor, early stopping on a validation split of *visitors* (70/15/15).
* **Planner:** scores -> normalised utility -> greedy selection maximising `utility / (viewing + insertion walking time)` within 92% of the time budget ->
  nearest-neighbour + 2-opt ordering on the effort matrix -> turn-by-turn legs -> drop the weakest stop if the real schedule overruns.
  Mobility maps to routing mode (full = scenic Grand Staircase, avoid stairs, wheelchair = step-free).
* **Results on 450 held-out simulated visitors:**

| Ranker | NDCG@10 | Precision@10 (grade>=2) |
|---|---|---|
| **XGBoost** | **0.834** | **0.716** |
| Hand-written rule (era + interest) | 0.781 | 0.663 |
| Popularity only | 0.272 | 0.223 |
| Random | 0.193 | 0.159 |

Top features: era match, interest overlap, number of selected eras, popularity x highlights-mode. **Caveat:** labels are simulated, so these numbers show the model
recovers the preference structure under noise; they are not evidence of real visitor satisfaction. Real feedback loop: thumbs up/down -> `/api/feedback` -> retrain.

## 5. Module 2 - indoor navigation
Weighted graph; edge cost = metres x (1 + 0.8 x crowd) for walking, stairs x penalty (x0.6 scenic / x2.2 easiest / x8 avoid / removed step-free), lift = length + wait.
Dijkstra with cached single-source runs; instructions derive left/right turns from heading change and merge stairs/lift segments. Tests: graph connectivity, step-free reachability of every zone, symmetry, mode behaviour.

## 6. Module 3 - AI artifact collections
Text = name + description + themes. Backends: CLIP ViT-B/32 (text + image, fused) or TF-IDF+SVD (shipped). K-Means with k chosen by cosine silhouette (k=12);
DBSCAN (cosine, eps 0.45, min_samples 2) marks 27 one-of-a-kind artifacts. Cluster labels come from dominant interest tags, object type and era purity.
Metrics (TF-IDF backend): silhouette 0.122, NMI vs category 0.56, NMI vs era 0.26. Low silhouette is expected for a 126-document corpus with bag-of-words vectors; re-run with CLIP (and photos)
and report the new numbers. Figure: `docs/figures/artifact_clusters.png`. Endpoints: collections, map, similar, classify (assign a new description to a collection).

## 7. Testing
`pytest`: 17 tests (dataset integrity, graph connectivity, routing modes, time-budget compliance, wheelchair no-stairs, interest/era sensitivity, API end-to-end). Dart: `gem_app/test/widget_test.dart` (offline router).

## 8. Limitations and future work
Schematic coordinates -> survey real plan; synthetic training labels -> collect feedback; CLIP run + real photos; live crowd data; indoor positioning (BLE/Wi-Fi/QR) for automatic "I am here"; Arabic localisation.
