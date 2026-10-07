"""Rebuild EVERYTHING from scratch:  python scripts/build_all.py [--backend auto|clip|tfidf]"""
import argparse, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--backend", default="auto")
a = ap.parse_args()
for step in (["build_dataset.py"], ["simulate_visitors.py"], ["train_tour_model.py"],
             ["build_clusters.py", "--backend", a.backend], ["export_app_assets.py"]):
    print("\n=== ", " ".join(step))
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts", step[0])] + step[1:], cwd=ROOT)
print("\nAll done. Start the API:  uvicorn backend.main:app --host 0.0.0.0 --port 8000")
