
import hashlib
import json
from pathlib import Path

CACHE_DIR = Path("data/cache/github")

def cache_path(key: str) -> Path:
    digest = hashlib.sha256(key.encode()).hexdigest()[:32]
    return CACHE_DIR / f"{digest}.json"


def cache_get(key: str):
    path = cache_path(key)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def cache_put(key:str, value):
    path = cache_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f)

