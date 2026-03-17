import os
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from src.collectors import Article
from src.main import collect_all, resolve_target_date


def _article(url: str, source: str = "hackernews") -> Article:
    return Article(url=url, title=f"Title {url}", source=source)


TARGET_DATE = date(2026, 1, 1)


@patch("src.main.hackernews")
@patch("src.main.techcrunch")
@patch("src.main.zenn")
@patch("src.main.qiita")
def test_deduplicates_by_url(mock_qiita, mock_zenn, mock_tc, mock_hn):
    shared_url = "https://example.com/shared"
    mock_hn.collect.return_value = [_article(shared_url, "hackernews")]
    mock_tc.collect.return_value = [_article(shared_url, "techcrunch")]
    mock_zenn.collect.return_value = []
    mock_qiita.collect.return_value = []

    articles = collect_all(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].url == shared_url


@patch("src.main.hackernews")
@patch("src.main.techcrunch")
@patch("src.main.zenn")
@patch("src.main.qiita")
def test_preserves_first_occurrence_on_dedup(mock_qiita, mock_zenn, mock_tc, mock_hn):
    shared_url = "https://example.com/shared"
    mock_hn.collect.return_value = [_article(shared_url, "hackernews")]
    mock_tc.collect.return_value = [_article(shared_url, "techcrunch")]
    mock_zenn.collect.return_value = []
    mock_qiita.collect.return_value = []

    articles = collect_all(TARGET_DATE)

    assert articles[0].source == "hackernews"


@patch("src.main.hackernews")
@patch("src.main.techcrunch")
@patch("src.main.zenn")
@patch("src.main.qiita")
def test_continues_when_collector_raises(mock_qiita, mock_zenn, mock_tc, mock_hn):
    mock_hn.collect.side_effect = RuntimeError("network error")
    mock_hn.__name__ = "hackernews"
    mock_tc.collect.return_value = [_article("https://techcrunch.com/ai", "techcrunch")]
    mock_zenn.collect.return_value = []
    mock_qiita.collect.return_value = []

    articles = collect_all(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].source == "techcrunch"


@patch("src.main.hackernews")
@patch("src.main.techcrunch")
@patch("src.main.zenn")
@patch("src.main.qiita")
def test_aggregates_all_sources(mock_qiita, mock_zenn, mock_tc, mock_hn):
    mock_hn.collect.return_value = [_article("https://hn.com/1", "hackernews")]
    mock_tc.collect.return_value = [_article("https://tc.com/1", "techcrunch")]
    mock_zenn.collect.return_value = [_article("https://zenn.dev/1", "zenn")]
    mock_qiita.collect.return_value = [_article("https://qiita.com/1", "qiita")]

    articles = collect_all(TARGET_DATE)

    sources = {a.source for a in articles}
    assert sources == {"hackernews", "techcrunch", "zenn", "qiita"}


@patch("src.main.hackernews")
@patch("src.main.techcrunch")
@patch("src.main.zenn")
@patch("src.main.qiita")
def test_collect_all_passes_date_to_each_collector(mock_qiita, mock_zenn, mock_tc, mock_hn):
    target = date(2026, 3, 10)
    for m in [mock_hn, mock_tc, mock_zenn, mock_qiita]:
        m.collect.return_value = []

    collect_all(target)

    mock_hn.collect.assert_called_once_with(target)
    mock_tc.collect.assert_called_once_with(target)
    mock_zenn.collect.assert_called_once_with(target)
    mock_qiita.collect.assert_called_once_with(target)


def test_resolve_target_date_reads_env_var():
    with patch.dict(os.environ, {"TARGET_DATE": "2026-03-10"}):
        assert resolve_target_date() == date(2026, 3, 10)


def test_resolve_target_date_defaults_to_yesterday():
    env = {k: v for k, v in os.environ.items() if k != "TARGET_DATE"}
    with patch.dict(os.environ, env, clear=True):
        assert resolve_target_date() == date.today() - timedelta(days=1)
