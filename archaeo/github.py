
import os

import requests
from dotenv import load_dotenv
from archaeo.cache import cache_get, cache_put
load_dotenv()

API_ROOT = "https://api.github.com"

def auth_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def fetch(url: str):
    cached_response = cache_get(url)
    if cached_response is not None:
        return cached_response

    response = requests.get(url, headers=auth_headers(), timeout=30)
    response.raise_for_status()
    data = response.json()
    cache_put(url, data)
    return data

