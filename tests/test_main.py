from unittest.mock import MagicMock, patch

from src.collectors import Article
from src.main import collect_all


def _article(url: str, source: str = "hackernews") -> Article:
    return Article(url=url, title=f"Title {url}", source=source)


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

    articles = collect_all()

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

    articles = collect_all()

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

    articles = collect_all()

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

    articles = collect_all()

    sources = {a.source for a in articles}
    assert sources == {"hackernews", "techcrunch", "zenn", "qiita"}
