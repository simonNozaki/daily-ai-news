from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.collectors import Article
from src.notebooklm_client import run_notebooklm


TARGET_DATE = date(2026, 1, 1)


def _make_articles(n: int = 2) -> list[Article]:
    return [Article(url=f"https://example.com/{i}", title=f"Article {i}", source="hackernews") for i in range(n)]


def _make_mock_client(notebook_id: str = "nb-123") -> MagicMock:
    nb = MagicMock()
    nb.id = notebook_id

    status = MagicMock()
    status.task_id = "task-1"

    client = MagicMock()
    client.notebooks.create = AsyncMock(return_value=nb)
    client.sources.add_url = AsyncMock()
    client.artifacts.generate_audio = AsyncMock(return_value=status)
    client.artifacts.wait_for_completion = AsyncMock()
    return client


@pytest.mark.asyncio
@patch("src.notebooklm_client.NotebookLMClient")
async def test_creates_notebook_with_todays_date(mock_cls):
    client = _make_mock_client()
    mock_cls.from_storage = AsyncMock(return_value=MagicMock(
        __aenter__=AsyncMock(return_value=client),
        __aexit__=AsyncMock(return_value=False),
    ))

    await run_notebooklm(_make_articles(), TARGET_DATE)

    client.notebooks.create.assert_called_once_with(f"AI News {TARGET_DATE.isoformat()}")


@pytest.mark.asyncio
@patch("src.notebooklm_client.NotebookLMClient")
async def test_adds_url_for_each_article(mock_cls):
    client = _make_mock_client()
    mock_cls.from_storage = AsyncMock(return_value=MagicMock(
        __aenter__=AsyncMock(return_value=client),
        __aexit__=AsyncMock(return_value=False),
    ))
    articles = _make_articles(3)

    await run_notebooklm(articles, TARGET_DATE)

    assert client.sources.add_url.call_count == 3
    called_urls = [call.args[1] for call in client.sources.add_url.call_args_list]
    assert called_urls == [a.url for a in articles]


@pytest.mark.asyncio
@patch("src.notebooklm_client.NotebookLMClient")
async def test_generates_podcast(mock_cls):
    client = _make_mock_client("nb-456")
    mock_cls.from_storage = AsyncMock(return_value=MagicMock(
        __aenter__=AsyncMock(return_value=client),
        __aexit__=AsyncMock(return_value=False),
    ))

    await run_notebooklm(_make_articles(), TARGET_DATE)

    client.artifacts.generate_audio.assert_called_once_with("nb-456")
    client.artifacts.wait_for_completion.assert_called_once_with("nb-456", "task-1")


@pytest.mark.asyncio
@patch("src.notebooklm_client.NotebookLMClient")
async def test_returns_notebook_id(mock_cls):
    client = _make_mock_client("nb-789")
    mock_cls.from_storage = AsyncMock(return_value=MagicMock(
        __aenter__=AsyncMock(return_value=client),
        __aexit__=AsyncMock(return_value=False),
    ))

    result = await run_notebooklm(_make_articles(), TARGET_DATE)

    assert result == "nb-789"
