from datetime import date
from unittest.mock import MagicMock, patch

from src.collectors.techcrunch import collect


def _make_entry(title: str, link: str) -> dict:
    return {"title": title, "link": link}


def _mock_feed(entries: list[dict]) -> MagicMock:
    feed = MagicMock()
    feed.entries = entries
    return feed


TARGET_DATE = date(2026, 1, 1)


@patch("src.collectors.techcrunch.feedparser.parse")
def test_returns_ai_articles(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("OpenAI releases GPT-5", "https://techcrunch.com/gpt5"),
    ])

    articles = collect(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].title == "OpenAI releases GPT-5"
    assert articles[0].source == "techcrunch"


@patch("src.collectors.techcrunch.feedparser.parse")
def test_filters_non_ai_articles(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("New startup gets funding", "https://techcrunch.com/startup"),
        _make_entry("AI startup raises $10M", "https://techcrunch.com/ai-startup"),
    ])

    articles = collect(TARGET_DATE)

    assert len(articles) == 1
    assert "AI" in articles[0].title


@patch("src.collectors.techcrunch.feedparser.parse")
def test_keyword_match_is_case_insensitive(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("machine learning advances", "https://techcrunch.com/ml"),
        _make_entry("LLM benchmark results", "https://techcrunch.com/llm"),
    ])

    articles = collect(TARGET_DATE)

    assert len(articles) == 2


@patch("src.collectors.techcrunch.feedparser.parse")
def test_caps_at_max_articles(mock_parse):
    entries = [
        _make_entry(f"AI story {i}", f"https://techcrunch.com/{i}") for i in range(10)
    ]
    mock_parse.return_value = _mock_feed(entries)

    articles = collect(TARGET_DATE)

    assert len(articles) == 3


@patch("src.collectors.techcrunch.feedparser.parse")
def test_skips_entry_without_link(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("AI news", ""),
    ])

    assert collect(TARGET_DATE) == []
