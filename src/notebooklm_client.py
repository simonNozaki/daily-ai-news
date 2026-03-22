import logging
from datetime import date

from notebooklm import NotebookLMClient

from .collectors import Article

logger = logging.getLogger(__name__)


async def run_notebooklm(articles: list[Article], target_date: date) -> str:
    today = target_date.isoformat()

    async with await NotebookLMClient.from_storage() as client:
        # 1. Set output language to Japanese
        await client.settings.set_output_language("ja")

        # 2. Create notebook
        nb = await client.notebooks.create(f"AI News {today}")

        # 3. Add URLs one by one, skipping failures
        for article in articles:
            try:
                await client.sources.add_url(nb.id, article.url, wait=True)
            except Exception:
                logger.warning("Failed to add source: %s", article.url, exc_info=True)

        # 4. Generate podcast
        status = await client.artifacts.generate_audio(nb.id)
        try:
            await client.artifacts.wait_for_completion(nb.id, status.task_id)
        except TimeoutError:
            logger.warning(
                "Audio generation timed out for notebook %s (task_id=%s)."
                " The notebook was created successfully but audio may still be processing.",
                nb.id,
                status.task_id,
            )

    return nb.id
