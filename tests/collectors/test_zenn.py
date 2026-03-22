from datetime import date
from unittest.mock import MagicMock, patch

from src.collectors.zenn import collect


def _mock_response(articles: list[dict]) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = {"articles": articles}
    return resp


def _article(title: str, path: str, published_at: str) -> dict:
    return {"title": title, "path": path, "published_at": published_at}


TARGET_DATE = date(2026, 1, 1)


@patch("src.collectors.zenn.httpx.Client")
def test_returns_articles(mock_client_cls):
    items = [_article("AIで変わる未来", "/user/articles/abc", "2026-01-01T12:00:00.000+09:00")]
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response(items)

    articles = collect(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].title == "AIで変わる未来"
    assert articles[0].source == "zenn"


@patch("src.collectors.zenn.httpx.Client")
def test_builds_url_from_path(mock_client_cls):
    items = [_article("AI記事", "/user/articles/slug123", "2026-01-01T10:00:00.000+09:00")]
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response(items)

    articles = collect(TARGET_DATE)

    assert articles[0].url == "https://zenn.dev/user/articles/slug123"


@patch("src.collectors.zenn.httpx.Client")
def test_caps_at_max_articles(mock_client_cls):
    items = [
        _article(f"Article {i}", f"/user/articles/{i}", "2026-01-01T10:00:00.000+09:00")
        for i in range(10)
    ]
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response(items)

    articles = collect(TARGET_DATE)

    assert len(articles) == 3


@patch("src.collectors.zenn.httpx.Client")
def test_filters_by_target_date(mock_client_cls):
    items = [
        _article("今日の記事", "/user/articles/today", "2026-01-01T10:00:00.000+09:00"),
        _article("昨日の記事", "/user/articles/yesterday", "2025-12-31T10:00:00.000+09:00"),
    ]
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response(items)

    articles = collect(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].title == "今日の記事"


@patch("src.collectors.zenn.httpx.Client")
def test_skips_entry_without_title(mock_client_cls):
    items = [_article("", "/user/articles/no-title", "2026-01-01T10:00:00.000+09:00")]
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response(items)

    assert collect(TARGET_DATE) == []


@patch("src.collectors.zenn.httpx.Client")
def test_empty_response_returns_empty_list(mock_client_cls):
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response([])

    assert collect(TARGET_DATE) == []


@patch("src.collectors.zenn.httpx.Client")
def test_skips_entry_without_path(mock_client_cls):
    items = [{"title": "パスなし記事", "published_at": "2026-01-01T10:00:00.000+09:00"}]
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response(items)

    assert collect(TARGET_DATE) == []


@patch("src.collectors.zenn.httpx.Client")
def test_uses_liked_order_in_request(mock_client_cls):
    mock_get = mock_client_cls.return_value.__enter__.return_value.get
    mock_get.return_value = _mock_response([])

    collect(TARGET_DATE)

    params = mock_get.call_args.kwargs["params"]
    assert params["order"] == "liked"
    assert params["topic_name"] == "ai"
