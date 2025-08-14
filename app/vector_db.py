import os
import faiss
import numpy as np
import json
from services.logger_setup import get_logger
from typing import Dict, List, Any
import re
from schemas import *
import openai
from collections import defaultdict


logger = get_logger(__name__)


def load_index():
    INDEX_PATH = os.getenv("INDEX_PATH", "database/travel_index.faiss")
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"Index file not found at {INDEX_PATH}")
    else:
        index = faiss.read_index(INDEX_PATH)
        logger.info(f"Loaded index with {index.ntotal} items")

        return index


def load_travel_items():
    METADATA_PATH = os.getenv("METADATA_PATH", "database/travel_metadata.json")
    if not os.path.exists(METADATA_PATH):
        raise FileNotFoundError(f"Metadata file not found at {METADATA_PATH}")
    else:
        with open(METADATA_PATH) as f:
            travel_items = json.load(f)

            return travel_items


def parse_flatten_seeds(text: str) -> Dict[str, str]:
    """
    Parse your flattened 'key: value - key: value ...' into a dict.
    Keeps the last occurrence of a key if repeated.
    """
    out = {}
    for part in text.split(" - "):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def to_float(x: Any, default: float = 0.0) -> float:
    try:
        # keep digits + dot only, e.g. "$149.00" -> "149.00"
        s = re.sub(r"[^0-9.]", "", str(x))
        return float(s) if s else default
    except Exception:
        return default


def pick_city(*vals) -> str:
    for v in vals:
        if v and str(v).strip():
            return str(v).strip()
    return "Unknown"


def query_emb(query):
    # query = "romantic hotel with sea view and spa in dubai with some activities, flight from london"
    query_vec = openai.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding
    query_vec = np.array(query_vec, dtype="float32")
    return query_vec


def top1_per_category(index, items, query_vec, pool=120) -> Dict:
    q = np.asarray(query_vec, dtype="float32").reshape(1, -1)
    k = min(pool, len(items))
    D, I = index.search(q, k)
    per_cat = {}
    for dist, idx in zip(D[0], I[0]):
        cat = items[idx]["category"]
        if cat not in per_cat:
            per_cat[cat] = {**items[idx], "_dist": float(dist)}
        if len(per_cat) == 3:  # flights, hotels, experiences (adjust if more)
            break
    return per_cat



def topk_per_category(index, items, query_vec, k_per_cat=1, pool=100):
    """
    index: FAISS index (built over all items in order)
    items: list[dict] with 'category'
    query_vec: 1D numpy array (embedding for the query)
    k_per_cat: how many to return per category
    pool: how many total neighbors to fetch before slicing by category
    """
    # ensure shape (1, dim)
    q = np.asarray(query_vec, dtype="float32").reshape(1, -1)
    # if you built an IndexFlatIP with normalized vectors, normalize q too:
    # faiss.normalize_L2(q)

    # pull a reasonably large pool once
    k = min(pool, len(items))
    D, I = index.search(q, k)

    per_cat = defaultdict(list)
    for dist, idx in zip(D[0], I[0]):
        cat = items[idx]["category"]
        if len(per_cat[cat]) < k_per_cat:
            per_cat[cat].append({"item": items[idx], "distance": float(dist)})
        # early exit if we’ve collected all categories up to k_per_cat
        if all(len(v) >= k_per_cat for v in per_cat.values()):
            break

    return per_cat