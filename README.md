# GEM Smart Navigation System - Grand Egyptian Museum

Mobile app (Flutter) + AI backend (Python / FastAPI) with three modules:

| Module | What it does | Tech |
|---|---|---|
| **1. AI Tour Customisation** | The visitor answers 9 questions (time, periods, interests, who is visiting, pace, depth, mobility, crowds, start point). The model ranks all artifacts, a planner fits them into the time budget and orders the stops. | **XGBoost** `XGBRanker` (rank:ndcg) + time-budgeted greedy selection + 2-opt route ordering |
| **2. Indoor Navigation** | Pick where you are and where you want to go -> easiest route with turn-by-turn steps, floor-by-floor plan drawing, step-free mode. | Graph model of the museum (50 zones, 72 links) + Dijkstra with stairs/lift/crowd costs. Also runs **on the phone** (offline). |
| **3. AI Artifact Collections** | Artifacts are grouped into thematic collections, with a similarity map and "similar artifacts". | **CLIP ViT-B/32** text+image embeddings (auto fallback: TF-IDF+SVD) -> **K-Means** (groups) + **DBSCAN** (one-of-a-kind outliers) |

```
GEM_Smart_Navigation_System/
├── data/                  datasets (artifacts.csv, zones.csv, edges.csv, questionnaire.json, visitor_profiles.csv,
│                          tour_training_data.csv.gz) + DATA_SOURCES.md (provenance - read it!)
├── gemcore/               shared Python logic (layout, navigation, features, planner, embeddings)
├── scripts/               build_dataset / simulate_visitors / train_tour_model / build_clusters / export_app_assets / build_all
├── models/                tour_ranker.json (XGBoost), artifact_clusters.json, metrics
├── backend/main.py        FastAPI server  (docs at /docs)
├── tests/                 17 automated tests (pytest)
├── gem_app/               Flutter app (your original screens + 3 new modules)
└── docs/                  PROJECT_REPORT.md, figures/
```

## 1. Run the backend (5 minutes)

```bash
cd GEM_Smart_Navigation_System
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
./run_backend.sh            # Windows: run_backend.bat      (or: uvicorn backend.main:app --host 0.0.0.0 --port 8000)
```
Open http://localhost:8000/docs to try every endpoint. Trained models and datasets are **already included** - nothing else is required.

Run the tests: `python -m pytest -q tests` (expected: 17 passed).
Rebuild everything from scratch (dataset -> training -> clustering -> app assets): `python scripts/build_all.py`.

## 2. Run the app

Requirements: Flutter SDK >= 3.22 (Dart >= 3.3).
```bash
cd gem_app
flutter create .            # one-time: regenerates any missing platform files (keeps your code & assets)
flutter pub get
flutter run                 # Android emulator: backend reachable at http://10.0.2.2:8000 (default)
```
* **Real phone:** connect phone and PC to the same Wi-Fi, then in the app open the drawer menu -> *Server address* and type `http://<PC-IP>:8000` (tap *Save & test*). Or: `flutter run --dart-define=GEM_API=http://192.168.1.20:8000`.
* **iOS simulator / desktop:** use `http://localhost:8000`.
* **No server?** The app still works in demo mode: indoor navigation is computed on the phone, AI Collections load from bundled JSON, and the tour screen shows the closest of 6 pre-generated tours. The UI tells the user when it is in demo mode.

App tabs: **Home** (your original) - **Navigate** (new indoor navigation) - **My Tour** (new AI tour) - **Exhibits** (featured viewer + new AI Collections) - **Tickets**. AI Chat moved to the drawer menu.

## 3. Demo script for your presentation
1. *My Tour*: choose 2 h, Tutankhamun + New Kingdom, interests Gold & Royalty -> show stops, "why recommended", match %, floor plan. Repeat with *Family* + *Wheelchair* to show the tour change (no stairs).
2. Tap **Navigate here** on a stop -> the Navigate tab opens with the route already computed.
3. *Navigate*: from Main Entrance to Gallery 12, compare *Easiest / Shortest / Step-free*; use *Nearest restroom*.
4. *Exhibits -> AI Collections*: open a group, open an artifact, show "Similar artifacts", then the *Similarity map* (X = DBSCAN outliers).
5. Show `http://localhost:8000/docs` and `docs/figures/artifact_clusters.png`.

## 4. Important limitations (be upfront in your report)
* **Floor-plan coordinates are schematic.** The topology (12 main galleries as 4 eras x 3 themes, Grand Staircase, Tutankhamun galleries, Khufu boats, etc.) follows public descriptions; metres are estimates. Replace them in `gemcore/layout.py` with the official plan and re-run `scripts/build_all.py`.
* **The XGBoost model is trained on synthetic visitors** (no real visitor logs exist yet). Reported scores measure how well it learns the simulated preference rules - not real-world satisfaction. The app already has thumbs-up/down feedback -> `/api/feedback` -> `scripts/export_feedback.py` -> retrain on real labels.
* **Dataset provenance:** see `data/DATA_SOURCES.md`. 43 rows are named in the official ticketing site/press/scholarly reviews; 80 are *representative* object types per gallery that must be verified against the museum catalogue.
* **CLIP could not be executed in the build environment** (no model download), so the shipped clusters use the TF-IDF+SVD fallback. On your machine: `pip install torch transformers pillow` then `python scripts/build_clusters.py --backend clip` (and optionally add photos with `scripts/fetch_images.py`).
* **The Flutter code was syntax-checked but not compiled/run** in the build environment (no Flutter SDK). Expect to fix small issues on first `flutter run`; all logic is plain Dart and mirrors the tested Python.
