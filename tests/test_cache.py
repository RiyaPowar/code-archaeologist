import pytest

from archaeo import cache

@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

def test_put_then_get_roundtrip():
    value = {"number": 12, "title": "Fix crash", "labels": ["bug"]}
    cache.cache_put("https://api.github.com/repos/x/y/issues/12", value)
    assert cache.cache_get("https://api.github.com/repos/x/y/issues/12") == value

def test_get_missing_key_returns_none():
    assert cache.cache_get("never-stored") is None