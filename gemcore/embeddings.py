"""
Embedding backends for the artifact exhibition module.

  clip   : OpenAI CLIP ViT-B/32 (HuggingFace `transformers`). Text = name + description,
           Image = data/images/<artifact_id>.jpg when present. Final vector = L2-normalised average of the
           text and image embeddings (text only when no image is available).
  tfidf  : TF-IDF + truncated SVD fallback (pure scikit-learn, no download). Used automatically when CLIP
           weights cannot be downloaded (offline machine) so the whole project always runs.

Switch with:  python scripts/build_clusters.py --backend clip
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.preprocessing import normalize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOP = sorted(set(ENGLISH_STOP_WORDS) | {"egypt", "egyptian", "ancient", "king", "museum", "period", "shows", "show", "dynasty", "found", "used", "themes"})


def artifact_text(row) -> str:
    """Text used for embeddings: name + description + human-readable themes (no metadata boilerplate)."""
    themes = ", ".join(t.replace("_", " ") for t in str(row["interest_tags"]).split(";"))
    return f"{row['name']}. {row['description']} Themes: {themes}."


class TfidfEmbedder:
    name = "tfidf-svd"

    def __init__(self, dim: int = 48):
        self.dim = dim
        self.vec = TfidfVectorizer(stop_words=STOP, ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        self.svd = None

    def fit_transform(self, art: pd.DataFrame) -> np.ndarray:
        X = self.vec.fit_transform([artifact_text(r) for _, r in art.iterrows()])
        self.svd = TruncatedSVD(n_components=min(self.dim, X.shape[1] - 1, X.shape[0] - 1), random_state=0)
        return normalize(self.svd.fit_transform(X))

    def transform_text(self, texts: list[str]) -> np.ndarray:
        return normalize(self.svd.transform(self.vec.transform(texts)))


class ClipEmbedder:
    name = "clip-vit-b32"

    def __init__(self, model_id="openai/clip-vit-base-patch32"):
        import torch  # noqa
        from transformers import CLIPModel, CLIPProcessor
        self.torch = torch
        self.model = CLIPModel.from_pretrained(model_id).eval()
        self.proc = CLIPProcessor.from_pretrained(model_id)

    def _text(self, texts):
        with self.torch.no_grad():
            t = self.proc(text=texts, return_tensors="pt", padding=True, truncation=True, max_length=77)
            e = self.model.get_text_features(**t)
        return normalize(e.numpy())

    def _image(self, paths):
        from PIL import Image
        imgs = [Image.open(p).convert("RGB") for p in paths]
        with self.torch.no_grad():
            e = self.model.get_image_features(**self.proc(images=imgs, return_tensors="pt"))
        return normalize(e.numpy())

    def fit_transform(self, art: pd.DataFrame) -> np.ndarray:
        texts = [artifact_text(r) for _, r in art.iterrows()]
        T = np.vstack([self._text(texts[i:i + 32]) for i in range(0, len(texts), 32)])
        E = T.copy()
        have = [(i, os.path.join(ROOT, p)) for i, p in enumerate(art["image_file"]) if os.path.exists(os.path.join(ROOT, p))]
        if have:
            idx, paths = zip(*have)
            I = self._image(list(paths))
            E[list(idx)] = normalize(T[list(idx)] + I)
        print(f"CLIP: text embeddings for {len(texts)} artifacts, image embeddings for {len(have)}")
        self._text_cache = T
        return E

    def transform_text(self, texts):
        return self._text(texts)


def get_embedder(backend: str = "auto"):
    if backend in ("clip", "auto"):
        try:
            return ClipEmbedder()
        except Exception as exc:          # no torch / no weights / offline
            if backend == "clip":
                raise
            print(f"[embeddings] CLIP unavailable ({type(exc).__name__}); falling back to TF-IDF+SVD")
    return TfidfEmbedder()
