import httpx
from datetime import date, datetime, timedelta, timezone

from . import Article

HN_API = "https://hn.algolia.com/api/v1/search"
MAX_ARTICLES = 5


def collect(target_date: date) -> list[Article]:
    start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    params = {
        "query": "AI",
        "tags": "story",
        "numericFilters": f"created_at_i>{int(start.timestamp())},created_at_i<{int(end.timestamp())}",
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
