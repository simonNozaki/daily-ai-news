from datetime import date
from unittest.mock import MagicMock, patch

from src.collectors.itmedia_ai import collect


def _make_entry(title: str, link: str) -> dict:
    return {"title": title, "link": link}


def _mock_feed(entries: list[dict]) -> MagicMock:
    feed = MagicMock()
    feed.entries = entries
    return feed


TARGET_DATE = date(2026, 1, 1)


@patch("src.collectors.itmedia_ai.feedparser.parse")
def test_returns_articles(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("生成AIの最新動向", "https://www.itmedia.co.jp/aiplus/articles/2601/01/news001.html"),
    ])

    articles = collect(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].title == "生成AIの最新動向"
    assert articles[0].source == "itmedia_ai"


@patch("src.collectors.itmedia_ai.feedparser.parse")
def test_caps_at_max_articles(mock_parse):
    entries = [_make_entry(f"AI記事{i}", f"https://www.itmedia.co.jp/aiplus/{i}") for i in range(10)]
    mock_parse.return_value = _mock_feed(entries)

    articles = collect(TARGET_DATE)

    assert len(articles) == 3


@patch("src.collectors.itmedia_ai.feedparser.parse")
def test_skips_entry_without_link(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("AIニュース", ""),
    ])

    assert collect(TARGET_DATE) == []


@patch("src.collectors.itmedia_ai.feedparser.parse")
def test_skips_entry_without_title(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("", "https://www.itmedia.co.jp/aiplus/articles/001.html"),
    ])

    assert collect(TARGET_DATE) == []


@patch("src.collectors.itmedia_ai.feedparser.parse")
def test_empty_feed_returns_empty_list(mock_parse):
    mock_parse.return_value = _mock_feed([])

    assert collect(TARGET_DATE) == []
