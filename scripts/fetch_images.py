"""Download artifact photos so the CLIP *image* encoder can be used.
1. Fill the `image_url` column of data/artifacts.csv (e.g. from the museum website / your own photos).
2. python scripts/fetch_images.py        -> saves data/images/<artifact_id>.jpg
3. python scripts/build_clusters.py --backend clip   (text + image embeddings are fused)"""
import os, sys, urllib.request
import pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
art = pd.read_csv(os.path.join(ROOT, "data", "artifacts.csv")).fillna("")
os.makedirs(os.path.join(ROOT, "data", "images"), exist_ok=True)
n = 0
for r in art.to_dict("records"):
    if not r["image_url"]:
        continue
    dst = os.path.join(ROOT, r["image_file"])
    if os.path.exists(dst):
        continue
    try:
        req = urllib.request.Request(r["image_url"], headers={"User-Agent": "Mozilla/5.0"})
        open(dst, "wb").write(urllib.request.urlopen(req, timeout=20).read())
        n += 1
    except Exception as exc:
        print("failed", r["artifact_id"], exc)
print("downloaded", n, "images")
