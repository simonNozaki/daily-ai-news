import httpx
from datetime import datetime, timedelta, timezone

from . import Article

HN_API = "https://hn.algolia.com/api/v1/search"
MAX_ARTICLES = 3


def collect() -> list[Article]:
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    since = int(yesterday.timestamp())

    params = {
        "query": "AI",
        "tags": "story",
        "numericFilters": f"created_at_i>{since}",
        "hitsPerPage": MAX_ARTICLES,
    }

    with httpx.Client(timeout=30) as client:
        resp = client.get(HN_API, params=params)
        resp.raise_for_status()
        data = resp.json()

    articles = []
    for hit in data.get("hits", []):
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}"
        title = hit.get("title", "")
        if url and title:
            articles.append(Article(url=url, title=title, source="hackernews"))

    return articles
