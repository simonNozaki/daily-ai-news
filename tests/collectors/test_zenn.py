from unittest.mock import MagicMock, patch

from src.collectors.zenn import collect


def _make_entry(title: str, link: str) -> dict:
    return {"title": title, "link": link}


def _mock_feed(entries: list[dict]) -> MagicMock:
    feed = MagicMock()
    feed.entries = entries
    return feed


@patch("src.collectors.zenn.feedparser.parse")
def test_returns_articles(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("AIで変わる未来", "https://zenn.dev/articles/abc"),
    ])

    articles = collect()

    assert len(articles) == 1
    assert articles[0].title == "AIで変わる未来"
    assert articles[0].source == "zenn"


@patch("src.collectors.zenn.feedparser.parse")
def test_caps_at_max_articles(mock_parse):
    entries = [_make_entry(f"Article {i}", f"https://zenn.dev/{i}") for i in range(10)]
    mock_parse.return_value = _mock_feed(entries)

    articles = collect()

    assert len(articles) == 3


@patch("src.collectors.zenn.feedparser.parse")
def test_skips_entry_without_url(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("Title only", ""),
    ])

    assert collect() == []


@patch("src.collectors.zenn.feedparser.parse")
def test_skips_entry_without_title(mock_parse):
    mock_parse.return_value = _mock_feed([
        _make_entry("", "https://zenn.dev/articles/no-title"),
    ])

    assert collect() == []


@patch("src.collectors.zenn.feedparser.parse")
def test_empty_feed_returns_empty_list(mock_parse):
    mock_parse.return_value = _mock_feed([])

    assert collect() == []
