import feedparser
from datetime import date

from . import Article

FEED_URL = "https://venturebeat.com/ai/feed/"
MAX_ARTICLES = 5


def collect(target_date: date) -> list[Article]:
    # target_date is not used for filtering: the VentureBeat AI feed is already
    # scoped to the AI category, so we simply take the latest MAX_ARTICLES entries.
    feed = feedparser.parse(FEED_URL)
    articles = []

    for entry in feed.entries:
        title = entry.get("title", "")
        url = entry.get("link", "")
        if url and title:
            articles.append(Article(url=url, title=title, source="venturebeat"))
        if len(articles) >= MAX_ARTICLES:
            break

    return articles
