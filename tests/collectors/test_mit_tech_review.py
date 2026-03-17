from datetime import date
from unittest.mock import MagicMock, patch

from src.collectors.mit_tech_review import collect


def _make_entry(title: str, link: str) -> dict:
    return {"title": title, "link": link}


def _mock_feed(entries: list[dict]) -> MagicMock:
    feed = MagicMock()
    feed.entries = entries
    return feed


TARGET_DATE = date(2026, 1, 1)


@patch("src.collectors.mit_tech_review.feedparser.parse")
def test_returns_ai_articles(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("The future of AI agents", "https://www.technologyreview.com/ai-agents"),
    ])

    articles = collect(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].title == "The future of AI agents"
    assert articles[0].source == "mit_tech_review"


@patch("src.collectors.mit_tech_review.feedparser.parse")
def test_filters_non_ai_articles(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("New battery technology breakthrough", "https://www.technologyreview.com/battery"),
        _make_entry("LLM benchmark results explained", "https://www.technologyreview.com/llm"),
    ])

    articles = collect(TARGET_DATE)

    assert len(articles) == 1
    assert "LLM" in articles[0].title


@patch("src.collectors.mit_tech_review.feedparser.parse")
def test_keyword_match_is_case_insensitive(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("machine learning in healthcare", "https://www.technologyreview.com/ml"),
        _make_entry("GPT-5 release date rumored", "https://www.technologyreview.com/gpt5"),
    ])

    articles = collect(TARGET_DATE)

    assert len(articles) == 2


@patch("src.collectors.mit_tech_review.feedparser.parse")
def test_caps_at_max_articles(mock_parse):
    entries = [
        _make_entry(f"AI story {i}", f"https://www.technologyreview.com/{i}") for i in range(10)
    ]
    mock_parse.return_value = _mock_feed(entries)

    articles = collect(TARGET_DATE)

    assert len(articles) == 3


@patch("src.collectors.mit_tech_review.feedparser.parse")
def test_skips_entry_without_link(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("AI news", ""),
    ])

    assert collect(TARGET_DATE) == []


@patch("src.collectors.mit_tech_review.feedparser.parse")
def test_empty_feed_returns_empty_list(mock_parse):
    mock_parse.return_value = _mock_feed([])

    assert collect(TARGET_DATE) == []
