from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch

from src.collectors.hackernews import collect


def _mock_response(hits: list[dict]) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = {"hits": hits}
    return resp


HIT = {"objectID": "42", "title": "AI Takes Over", "url": "https://example.com/ai"}
TARGET_DATE = date(2026, 1, 1)


@patch("src.collectors.hackernews.httpx.Client")
def test_returns_articles(mock_client_cls):
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response([HIT])

    articles = collect(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].url == "https://example.com/ai"
    assert articles[0].title == "AI Takes Over"
    assert articles[0].source == "hackernews"


@patch("src.collectors.hackernews.httpx.Client")
def test_fallback_url_when_url_missing(mock_client_cls):
    hit = {"objectID": "99", "title": "Ask HN: AI?", "url": None}
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response([hit])

    articles = collect(TARGET_DATE)

    assert articles[0].url == "https://news.ycombinator.com/item?id=99"


@patch("src.collectors.hackernews.httpx.Client")
def test_empty_hits_returns_empty_list(mock_client_cls):
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response([])

    assert collect(TARGET_DATE) == []


@patch("src.collectors.hackernews.httpx.Client")
def test_skips_entry_without_title(mock_client_cls):
    hit = {"objectID": "1", "title": "", "url": "https://example.com"}
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response([hit])

    assert collect(TARGET_DATE) == []


@patch("src.collectors.hackernews.httpx.Client")
def test_respects_max_articles(mock_client_cls):
    hits = [{"objectID": str(i), "title": f"AI Story {i}", "url": f"https://example.com/{i}"} for i in range(5)]
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response(hits)

    # MAX_ARTICLES=5 is enforced via hitsPerPage in the API request;
    # the collector returns whatever the API sends back.
    articles = collect(TARGET_DATE)
    assert len(articles) == 5  # collector trusts API to cap at hitsPerPage


@patch("src.collectors.hackernews.httpx.Client")
def test_sends_max_articles_as_hits_per_page(mock_client_cls):
    mock_get = mock_client_cls.return_value.__enter__.return_value.get
    mock_get.return_value = _mock_response([])

    collect(TARGET_DATE)

    params = mock_get.call_args.kwargs["params"]
    assert params["hitsPerPage"] == 5


@patch("src.collectors.hackernews.httpx.Client")
def test_uses_target_date_for_api_filter(mock_client_cls):
    mock_get = mock_client_cls.return_value.__enter__.return_value.get
    mock_get.return_value = _mock_response([])
    target = date(2026, 3, 10)

    collect(target)

    params = mock_get.call_args.kwargs["params"]
    expected_start = int(datetime(2026, 3, 10, tzinfo=timezone.utc).timestamp())
    expected_end = int(datetime(2026, 3, 11, tzinfo=timezone.utc).timestamp())
    assert f"created_at_i>{expected_start}" in params["numericFilters"]
    assert f"created_at_i<{expected_end}" in params["numericFilters"]
