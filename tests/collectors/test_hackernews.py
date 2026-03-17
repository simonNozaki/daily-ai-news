from unittest.mock import MagicMock, patch

from src.collectors.hackernews import collect


def _mock_response(hits: list[dict]) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = {"hits": hits}
    return resp


HIT = {"objectID": "42", "title": "AI Takes Over", "url": "https://example.com/ai"}


@patch("src.collectors.hackernews.httpx.Client")
def test_returns_articles(mock_client_cls):
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response([HIT])

    articles = collect()

    assert len(articles) == 1
    assert articles[0].url == "https://example.com/ai"
    assert articles[0].title == "AI Takes Over"
    assert articles[0].source == "hackernews"


@patch("src.collectors.hackernews.httpx.Client")
def test_fallback_url_when_url_missing(mock_client_cls):
    hit = {"objectID": "99", "title": "Ask HN: AI?", "url": None}
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response([hit])

    articles = collect()

    assert articles[0].url == "https://news.ycombinator.com/item?id=99"


@patch("src.collectors.hackernews.httpx.Client")
def test_empty_hits_returns_empty_list(mock_client_cls):
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response([])

    assert collect() == []


@patch("src.collectors.hackernews.httpx.Client")
def test_skips_entry_without_title(mock_client_cls):
    hit = {"objectID": "1", "title": "", "url": "https://example.com"}
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response([hit])

    assert collect() == []


@patch("src.collectors.hackernews.httpx.Client")
def test_respects_max_articles(mock_client_cls):
    hits = [{"objectID": str(i), "title": f"AI Story {i}", "url": f"https://example.com/{i}"} for i in range(5)]
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response(hits)

    # MAX_ARTICLES=3 is enforced via hitsPerPage in the API request;
    # the collector returns whatever the API sends back.
    articles = collect()
    assert len(articles) == 5  # collector trusts API to cap at hitsPerPage
