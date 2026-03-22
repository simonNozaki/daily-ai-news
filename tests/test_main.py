import logging
import os
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from src.collectors import Article
from src.main import collect_all, resolve_target_date


def _article(url: str, source: str = "hackernews") -> Article:
    return Article(url=url, title=f"Title {url}", source=source)


TARGET_DATE = date(2026, 1, 1)

ALL_COLLECTORS = [
    "src.main.hackernews",
    "src.main.techcrunch",
    "src.main.zenn",
    "src.main.qiita",
    "src.main.venturebeat",
    "src.main.a16z",
]


def _patch_all_collectors(returns: dict[str, list] | None = None):
    """全コレクターをまとめてpatchするコンテキストマネージャを返す。"""
    returns = returns or {}

    def decorator(fn):
        for path in reversed(ALL_COLLECTORS):
            fn = patch(path)(fn)
        return fn

    return decorator


@patch("src.main.a16z")
@patch("src.main.venturebeat")
@patch("src.main.qiita")
@patch("src.main.zenn")
@patch("src.main.techcrunch")
@patch("src.main.hackernews")
def test_deduplicates_by_url(mock_hn, mock_tc, mock_zenn, mock_qiita, mock_vb, mock_a16z):
    shared_url = "https://example.com/shared"
    mock_hn.collect.return_value = [_article(shared_url, "hackernews")]
    mock_tc.collect.return_value = [_article(shared_url, "techcrunch")]
    for m in [mock_zenn, mock_qiita, mock_vb, mock_a16z]:
        m.collect.return_value = []

    articles = collect_all(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].url == shared_url


@patch("src.main.a16z")
@patch("src.main.venturebeat")
@patch("src.main.qiita")
@patch("src.main.zenn")
@patch("src.main.techcrunch")
@patch("src.main.hackernews")
def test_preserves_first_occurrence_on_dedup(mock_hn, mock_tc, mock_zenn, mock_qiita, mock_vb, mock_a16z):
    shared_url = "https://example.com/shared"
    mock_hn.collect.return_value = [_article(shared_url, "hackernews")]
    mock_tc.collect.return_value = [_article(shared_url, "techcrunch")]
    for m in [mock_zenn, mock_qiita, mock_vb, mock_a16z]:
        m.collect.return_value = []

    articles = collect_all(TARGET_DATE)

    assert articles[0].source == "hackernews"


@patch("src.main.a16z")
@patch("src.main.venturebeat")
@patch("src.main.qiita")
@patch("src.main.zenn")
@patch("src.main.techcrunch")
@patch("src.main.hackernews")
def test_continues_when_collector_raises(mock_hn, mock_tc, mock_zenn, mock_qiita, mock_vb, mock_a16z):
    mock_hn.collect.side_effect = RuntimeError("network error")
    mock_hn.__name__ = "hackernews"
    mock_tc.collect.return_value = [_article("https://techcrunch.com/ai", "techcrunch")]
    for m in [mock_zenn, mock_qiita, mock_vb, mock_a16z]:
        m.collect.return_value = []

    articles = collect_all(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].source == "techcrunch"


@patch("src.main.a16z")
@patch("src.main.venturebeat")
@patch("src.main.qiita")
@patch("src.main.zenn")
@patch("src.main.techcrunch")
@patch("src.main.hackernews")
def test_collector_failure_is_logged_as_warning_with_traceback(
    mock_hn, mock_tc, mock_zenn, mock_qiita, mock_vb, mock_a16z, caplog
):
    mock_hn.collect.side_effect = RuntimeError("timeout")
    mock_hn.__name__ = "hackernews"
    for m in [mock_tc, mock_zenn, mock_qiita, mock_vb, mock_a16z]:
        m.collect.return_value = []

    with caplog.at_level(logging.WARNING, logger="src.main"):
        collect_all(TARGET_DATE)

    assert any("hackernews" in r.message for r in caplog.records)
    assert any(r.exc_info is not None for r in caplog.records)


@patch("src.main.a16z")
@patch("src.main.venturebeat")
@patch("src.main.qiita")
@patch("src.main.zenn")
@patch("src.main.techcrunch")
@patch("src.main.hackernews")
def test_aggregates_all_sources(mock_hn, mock_tc, mock_zenn, mock_qiita, mock_vb, mock_a16z):
    mock_hn.collect.return_value = [_article("https://hn.com/1", "hackernews")]
    mock_tc.collect.return_value = [_article("https://tc.com/1", "techcrunch")]
    mock_zenn.collect.return_value = [_article("https://zenn.dev/1", "zenn")]
    mock_qiita.collect.return_value = [_article("https://qiita.com/1", "qiita")]
    mock_vb.collect.return_value = [_article("https://venturebeat.com/1", "venturebeat")]
    mock_a16z.collect.return_value = [_article("https://a16z.com/1", "a16z")]

    articles = collect_all(TARGET_DATE)

    sources = {a.source for a in articles}
    assert sources == {"hackernews", "techcrunch", "zenn", "qiita", "venturebeat", "a16z"}


@patch("src.main.a16z")
@patch("src.main.venturebeat")
@patch("src.main.qiita")
@patch("src.main.zenn")
@patch("src.main.techcrunch")
@patch("src.main.hackernews")
def test_collect_all_passes_date_to_each_collector(mock_hn, mock_tc, mock_zenn, mock_qiita, mock_vb, mock_a16z):
    target = date(2026, 3, 10)
    for m in [mock_hn, mock_tc, mock_zenn, mock_qiita, mock_vb, mock_a16z]:
        m.collect.return_value = []

    collect_all(target)

    for m in [mock_hn, mock_tc, mock_zenn, mock_qiita, mock_vb, mock_a16z]:
        m.collect.assert_called_once_with(target)


@patch("src.main.a16z")
@patch("src.main.venturebeat")
@patch("src.main.qiita")
@patch("src.main.zenn")
@patch("src.main.techcrunch")
@patch("src.main.hackernews")
def test_logs_warning_when_all_collectors_return_empty(
    mock_hn, mock_tc, mock_zenn, mock_qiita, mock_vb, mock_a16z, caplog
):
    for m in [mock_hn, mock_tc, mock_zenn, mock_qiita, mock_vb, mock_a16z]:
        m.collect.return_value = []

    with caplog.at_level(logging.WARNING, logger="src.main"):
        result = collect_all(TARGET_DATE)

    assert result == []
    assert any(r.levelno == logging.WARNING for r in caplog.records)
    assert any("0" in r.message or "empty" in r.message.lower() or "記事" in r.message for r in caplog.records)


def test_resolve_target_date_reads_env_var():
    with patch.dict(os.environ, {"TARGET_DATE": "2026-03-10"}):
        assert resolve_target_date() == date(2026, 3, 10)


def test_resolve_target_date_defaults_to_yesterday():
    env = {k: v for k, v in os.environ.items() if k != "TARGET_DATE"}
    with patch.dict(os.environ, env, clear=True):
        assert resolve_target_date() == date.today() - timedelta(days=1)
