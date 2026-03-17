import feedparser
from datetime import date

from . import Article

FEED_URL = "https://www.technologyreview.com/feed/"
AI_KEYWORDS = {"ai", "artificial intelligence", "machine learning", "llm", "gpt", "openai", "deepmind", "gemini"}
MAX_ARTICLES = 3


def collect(target_date: date) -> list[Article]:
    feed = feedparser.parse(FEED_URL)
    articles = []

    for entry in feed.entries:
        title = entry.get("title", "")
        if any(kw in title.lower() for kw in AI_KEYWORDS):
            url = entry.get("link", "")
            if url and title:
                articles.append(Article(url=url, title=title, source="mit_tech_review"))
            if len(articles) >= MAX_ARTICLES:
                break

    return articles
