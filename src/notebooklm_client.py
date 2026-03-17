from datetime import date

from notebooklm import NotebookLMClient

from .collectors import Article


async def run_notebooklm(articles: list[Article]) -> str:
    today = date.today().isoformat()

    async with await NotebookLMClient.from_storage() as client:
        # 1. Create notebook
        nb = await client.notebooks.create(f"AI News {today}")

        # 2. Add URLs one by one
        for article in articles:
            await client.sources.add_url(nb.id, article.url, wait=True)

        # 3. Generate podcast
        status = await client.artifacts.generate_audio(nb.id)
        await client.artifacts.wait_for_completion(nb.id, status.task_id)

    return nb.id
