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
    "src.main.theverge",
    "src.main.mit_tech_review",
    "src.main.itmedia_ai",
]


def _patch_all_collectors(returns: dict[str, list] | None = None):
    """全コレクターをまとめてpatchするコンテキストマネージャを返す。"""
    returns = returns or {}

    def decorator(fn):
        for path in reversed(ALL_COLLECTORS):
            fn = patch(path)(fn)
        return fn

    return decorator


@patch("src.main.itmedia_ai")
@patch("src.main.mit_tech_review")
@patch("src.main.theverge")
@patch("src.main.qiita")
@patch("src.main.zenn")
@patch("src.main.techcrunch")
@patch("src.main.hackernews")
def test_deduplicates_by_url(mock_hn, mock_tc, mock_zenn, mock_qiita, mock_tv, mock_mtr, mock_itm):
    shared_url = "https://example.com/shared"
    mock_hn.collect.return_value = [_article(shared_url, "hackernews")]
    mock_tc.collect.return_value = [_article(shared_url, "techcrunch")]
    for m in [mock_zenn, mock_qiita, mock_tv, mock_mtr, mock_itm]:
        m.collect.return_value = []

    articles = collect_all(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].url == shared_url


@patch("src.main.itmedia_ai")
@patch("src.main.mit_tech_review")
@patch("src.main.theverge")
@patch("src.main.qiita")
@patch("src.main.zenn")
@patch("src.main.techcrunch")
@patch("src.main.hackernews")
def test_preserves_first_occurrence_on_dedup(mock_hn, mock_tc, mock_zenn, mock_qiita, mock_tv, mock_mtr, mock_itm):
    shared_url = "https://example.com/shared"
    mock_hn.collect.return_value = [_article(shared_url, "hackernews")]
    mock_tc.collect.return_value = [_article(shared_url, "techcrunch")]
    for m in [mock_zenn, mock_qiita, mock_tv, mock_mtr, mock_itm]:
        m.collect.return_value = []

    articles = collect_all(TARGET_DATE)

    assert articles[0].source == "hackernews"


@patch("src.main.itmedia_ai")
@patch("src.main.mit_tech_review")
@patch("src.main.theverge")
@patch("src.main.qiita")
@patch("src.main.zenn")
@patch("src.main.techcrunch")
@patch("src.main.hackernews")
def test_continues_when_collector_raises(mock_hn, mock_tc, mock_zenn, mock_qiita, mock_tv, mock_mtr, mock_itm):
    mock_hn.collect.side_effect = RuntimeError("network error")
    mock_hn.__name__ = "hackernews"
    mock_tc.collect.return_value = [_article("https://techcrunch.com/ai", "techcrunch")]
    for m in [mock_zenn, mock_qiita, mock_tv, mock_mtr, mock_itm]:
        m.collect.return_value = []

    articles = collect_all(TARGET_DATE)

    assert len(articles) == 1
    assert articles[0].source == "techcrunch"


@patch("src.main.itmedia_ai")
@patch("src.main.mit_tech_review")
@patch("src.main.theverge")
@patch("src.main.qiita")
@patch("src.main.zenn")
@patch("src.main.techcrunch")
@patch("src.main.hackernews")
def test_aggregates_all_sources(mock_hn, mock_tc, mock_zenn, mock_qiita, mock_tv, mock_mtr, mock_itm):
    mock_hn.collect.return_value = [_article("https://hn.com/1", "hackernews")]
    mock_tc.collect.return_value = [_article("https://tc.com/1", "techcrunch")]
    mock_zenn.collect.return_value = [_article("https://zenn.dev/1", "zenn")]
    mock_qiita.collect.return_value = [_article("https://qiita.com/1", "qiita")]
    mock_tv.collect.return_value = [_article("https://theverge.com/1", "theverge")]
    mock_mtr.collect.return_value = [_article("https://technologyreview.com/1", "mit_tech_review")]
    mock_itm.collect.return_value = [_article("https://itmedia.co.jp/1", "itmedia_ai")]

    articles = collect_all(TARGET_DATE)

    sources = {a.source for a in articles}
    assert sources == {"hackernews", "techcrunch", "zenn", "qiita", "theverge", "mit_tech_review", "itmedia_ai"}


@patch("src.main.itmedia_ai")
@patch("src.main.mit_tech_review")
@patch("src.main.theverge")
@patch("src.main.qiita")
@patch("src.main.zenn")
@patch("src.main.techcrunch")
@patch("src.main.hackernews")
def test_collect_all_passes_date_to_each_collector(mock_hn, mock_tc, mock_zenn, mock_qiita, mock_tv, mock_mtr, mock_itm):
    target = date(2026, 3, 10)
    for m in [mock_hn, mock_tc, mock_zenn, mock_qiita, mock_tv, mock_mtr, mock_itm]:
        m.collect.return_value = []

    collect_all(target)

    for m in [mock_hn, mock_tc, mock_zenn, mock_qiita, mock_tv, mock_mtr, mock_itm]:
        m.collect.assert_called_once_with(target)


def test_resolve_target_date_reads_env_var():
    with patch.dict(os.environ, {"TARGET_DATE": "2026-03-10"}):
        assert resolve_target_date() == date(2026, 3, 10)


def test_resolve_target_date_defaults_to_yesterday():
    env = {k: v for k, v in os.environ.items() if k != "TARGET_DATE"}
    with patch.dict(os.environ, env, clear=True):
        assert resolve_target_date() == date.today() - timedelta(days=1)
