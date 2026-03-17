import feedparser
from datetime import date

from . import Article

FEED_URL = "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml"
MAX_ARTICLES = 3


def collect(target_date: date) -> list[Article]:
    feed = feedparser.parse(FEED_URL)
    articles = []

    for entry in feed.entries[:MAX_ARTICLES]:
        url = entry.get("link", "")
        title = entry.get("title", "")
        if url and title:
            articles.append(Article(url=url, title=title, source="itmedia_ai"))

    return articles
