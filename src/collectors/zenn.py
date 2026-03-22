import httpx
from datetime import date

from . import Article

API_URL = "https://zenn.dev/api/articles"
MAX_ARTICLES = 5


def collect(target_date: date) -> list[Article]:
    params = {
        "order": "liked",
        "topic_name": "ai",
        "count": 20,
    }

    with httpx.Client(timeout=30) as client:
        resp = client.get(API_URL, params=params)
        resp.raise_for_status()
        items = resp.json().get("articles", [])

    target_dt = target_date.isoformat()
    articles = []
    for item in items:
        published_at = item.get("published_at", "")
        if not published_at.startswith(target_dt):
            continue
        path = item.get("path", "")
        if not path:
            continue
        url = f"https://zenn.dev{path}"
        title = item.get("title", "")
        if title:
            articles.append(Article(url=url, title=title, source="zenn"))
        if len(articles) >= MAX_ARTICLES:
            break

    return articles
