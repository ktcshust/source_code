# sentence-transformers / cross-encoder logic
import asyncio
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder
import numpy as np
from typing import Optional

# small caches to avoid reload every call
_EMBED_MODEL = None
_CROSS_ENCODER = None

def get_embed_model():
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        # a small, fast model for embeddings
        _EMBED_MODEL = SentenceTransformer("all-mpnet-base-v2")
    return _EMBED_MODEL

def get_cross_encoder():
    global _CROSS_ENCODER
    if _CROSS_ENCODER is None:
        try:
            _CROSS_ENCODER = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        except Exception:
            _CROSS_ENCODER = None
    return _CROSS_ENCODER

async def relevance_score(article_text: str, title: str | None = None) -> dict:
    """
    Returns a dict with relevance_score (float 0..1) and a boolean 'is_relevant'.
    Strategy:
      1) If CrossEncoder available -> use it to score text vs query 'AI news relevance'
      2) Else -> embeddings similarity to keyword centroid
    """
    text = (title or "") + "\n\n" + article_text
    ce = get_cross_encoder()
    if ce is not None:
        # Cross-encoder expects list of pairs [ (query, text) ]
        query = "This article is about AI / artificial intelligence / AI applications"
        scores = ce.predict([(query, text)])
        score = float(scores[0])
        # normalize: cross-encoder scores are higher -> map with sigmoid-ish or simple clamp
        is_rel = score > 0.5
        return {"relevance_score": score, "is_relevant": bool(is_rel), "method":"cross-encoder"}
    # fallback: embeddings + keyword centroid
    model = get_embed_model()
    emb = model.encode([text], convert_to_numpy=True)[0]
    # precompute keyword centroid
    keywords = [
        "artificial intelligence", "AI", "trí tuệ nhân tạo",
        "ứng dụng AI", "machine learning", "deep learning"
    ]
    kw_embs = model.encode(keywords, convert_to_numpy=True)
    centroid = np.mean(kw_embs, axis=0)
    # cosine
    cos = float(np.dot(emb, centroid) / (np.linalg.norm(emb) * np.linalg.norm(centroid) + 1e-9))
    is_rel = cos > 0.56  # threshold; tune on real data
    return {"relevance_score": float(cos), "is_relevant": bool(is_rel), "method":"embed-cos"}

