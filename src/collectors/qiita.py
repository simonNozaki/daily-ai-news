import httpx
from datetime import date

from . import Article

QIITA_API = "https://qiita.com/api/v2/items"
MAX_ARTICLES = 3


def collect(target_date: date) -> list[Article]:
    params = {
        "query": f"tag:AI created:>{target_date.isoformat()}",
        "per_page": 20,
    }

    with httpx.Client(timeout=30) as client:
        resp = client.get(QIITA_API, params=params)
        resp.raise_for_status()
        items = resp.json()

    # Sort by likes_count descending
    items.sort(key=lambda x: x.get("likes_count", 0), reverse=True)

    articles = []
    for item in items[:MAX_ARTICLES]:
        url = item.get("url", "")
        title = item.get("title", "")
        if url and title:
            articles.append(Article(url=url, title=title, source="qiita"))

    return articles
