from datetime import date
from unittest.mock import MagicMock, patch

from src.collectors.a16z import collect


def _make_entry(title: str, link: str) -> dict:
    return {"title": title, "link": link}


def _mock_feed(entries: list[dict]) -> MagicMock:
    feed = MagicMock()
    feed.entries = entries
    return feed


TARGET_DATE = date(2026, 1, 1)


@patch("src.collectors.a16z.feedparser.parse")
def test_returns_ai_articles(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("The Future of AI in Enterprise", "https://a16z.com/ai-enterprise"),
    ])

    articles = collect(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].title == "The Future of AI in Enterprise"
    assert articles[0].source == "a16z"


@patch("src.collectors.a16z.feedparser.parse")
def test_filters_non_ai_articles(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("Investing in Biotech", "https://a16z.com/biotech"),
        _make_entry("AI is transforming healthcare", "https://a16z.com/ai-healthcare"),
    ])

    articles = collect(TARGET_DATE)

    assert len(articles) == 1
    assert "AI" in articles[0].title


@patch("src.collectors.a16z.feedparser.parse")
def test_keyword_match_is_case_insensitive(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("machine learning at scale", "https://a16z.com/ml"),
        _make_entry("large language models explained", "https://a16z.com/llm"),
    ])

    articles = collect(TARGET_DATE)

    assert len(articles) == 2


@patch("src.collectors.a16z.feedparser.parse")
def test_caps_at_max_articles(mock_parse):
    entries = [
        _make_entry(f"AI story {i}", f"https://a16z.com/ai-{i}") for i in range(10)
    ]
    mock_parse.return_value = _mock_feed(entries)

    articles = collect(TARGET_DATE)

    assert len(articles) == 5


@patch("src.collectors.a16z.feedparser.parse")
def test_skips_entry_without_link(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("AI trends", ""),
    ])

    assert collect(TARGET_DATE) == []


@patch("src.collectors.a16z.feedparser.parse")
def test_empty_feed_returns_empty_list(mock_parse):
    mock_parse.return_value = _mock_feed([])

    assert collect(TARGET_DATE) == []
