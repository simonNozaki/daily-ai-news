import feedparser
from datetime import date

from . import Article

FEED_URL = "https://a16z.com/feed/"
AI_KEYWORDS = {"ai", "artificial intelligence", "machine learning", "llm", "gpt", "language model", "deep learning", "neural"}
MAX_ARTICLES = 5


def collect(target_date: date) -> list[Article]:
    # target_date is not used for filtering: a16z posts infrequently, so date
    # filtering would return empty results most days. We take the latest
    # MAX_ARTICLES AI-related entries instead.
    feed = feedparser.parse(FEED_URL)
    articles = []

    for entry in feed.entries:
        title = entry.get("title", "")
        url = entry.get("link", "")
        if not url:
            continue
        if any(kw in title.lower() for kw in AI_KEYWORDS):
            articles.append(Article(url=url, title=title, source="a16z"))
        if len(articles) >= MAX_ARTICLES:
            break

    return articles
