from datetime import date
from unittest.mock import MagicMock, patch

from src.collectors.qiita import collect


def _mock_response(items: list[dict]) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = items
    return resp


def _item(title: str, url: str, likes: int) -> dict:
    return {"title": title, "url": url, "likes_count": likes}


TARGET_DATE = date(2026, 1, 1)


@patch("src.collectors.qiita.httpx.Client")
def test_returns_articles(mock_client_cls):
    items = [_item("AI入門", "https://qiita.com/ai", 10)]
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response(items)

    articles = collect(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].title == "AI入門"
    assert articles[0].source == "qiita"


@patch("src.collectors.qiita.httpx.Client")
def test_sorted_by_likes_descending(mock_client_cls):
    items = [
        _item("Low likes", "https://qiita.com/low", 1),
        _item("High likes", "https://qiita.com/high", 100),
        _item("Mid likes", "https://qiita.com/mid", 50),
    ]
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response(items)

    articles = collect(TARGET_DATE)

    assert articles[0].title == "High likes"
    assert articles[1].title == "Mid likes"
    assert articles[2].title == "Low likes"


@patch("src.collectors.qiita.httpx.Client")
def test_caps_at_max_articles(mock_client_cls):
    items = [_item(f"Article {i}", f"https://qiita.com/{i}", i) for i in range(10)]
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response(items)

    articles = collect(TARGET_DATE)

    assert len(articles) == 3


@patch("src.collectors.qiita.httpx.Client")
def test_skips_entry_without_url(mock_client_cls):
    items = [_item("No URL", "", 5)]
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response(items)

    assert collect(TARGET_DATE) == []


@patch("src.collectors.qiita.httpx.Client")
def test_empty_response_returns_empty_list(mock_client_cls):
    mock_client_cls.return_value.__enter__.return_value.get.return_value = _mock_response([])

    assert collect(TARGET_DATE) == []


@patch("src.collectors.qiita.httpx.Client")
def test_uses_target_date_in_query(mock_client_cls):
    mock_get = mock_client_cls.return_value.__enter__.return_value.get
    mock_get.return_value = _mock_response([])
    target = date(2026, 3, 10)

    collect(target)

    params = mock_get.call_args.kwargs["params"]
    assert "created:>2026-03-10" in params["query"]
