import pytest

from archaeo import cache, github

class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data

@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

@pytest.fixture
def fake_get(monkeypatch):
    calls = []

    def _get(url, headers=None, timeout=None):
        calls.append(url)
        return FakeResponse({"url": url, "number": 12})

    monkeypatch.setattr(github.requests, "get", _get)
    return calls

def test_cache_miss_calls_network_once(fake_get):
    url = "https://api.github.com/repos/x/y/issues/12"
    data = github.fetch(url)
    assert data["number"] == 12
    assert fake_get == [url]

def test_cache_hit_skips_network(fake_get):
    url = "https://api.github.com/repos/x/y/issues/12"
    # First call to populate cache
    github.fetch(url)
    # Second call should hit cache
    data = github.fetch(url)
    assert data["number"] == 12
    assert len(fake_get) == 1  # Only one network call made

def test_failed_request_is_not_cached(monkeypatch):
    url = "https://api.github.com/repos/x/y/issues/404"
    calls = []

    class FailingResponse:
        def raise_for_status(self):
            raise github.requests.HTTPError("404 Not Found")

        def json(self):
            return {}

    def failing_get(url, headers=None, timeout=None):
        calls.append(url)
        return FailingResponse()

    monkeypatch.setattr(github.requests, "get", failing_get)

    # 1. The failure propagates and nothing is cached
    with pytest.raises(github.requests.HTTPError):
        github.fetch(url)
    assert cache.cache_get(url) is None

    # 2. Swap in a working fake: fetch must hit the network again
    def working_get(url, headers=None, timeout=None):
        calls.append(url)
        return FakeResponse({"number": 404})

    monkeypatch.setattr(github.requests, "get", working_get)

    data = github.fetch(url)
    assert data["number"] == 404
    assert calls == [url, url]  # one failed call + one successful call
