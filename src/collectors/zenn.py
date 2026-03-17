import feedparser

from . import Article

FEED_URL = "https://zenn.dev/topics/ai/feed"
MAX_ARTICLES = 3


def collect() -> list[Article]:
    feed = feedparser.parse(FEED_URL)
    articles = []

    for entry in feed.entries[:MAX_ARTICLES]:
        url = entry.get("link", "")
        title = entry.get("title", "")
        if url and title:
            articles.append(Article(url=url, title=title, source="zenn"))

    return articles
