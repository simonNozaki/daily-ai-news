import asyncio
import logging
import os
from datetime import date, timedelta

from dotenv import load_dotenv

from .collectors import Article
from .collectors import hackernews, techcrunch, zenn, qiita, venturebeat, a16z
from .notebooklm_client import run_notebooklm

load_dotenv()

logger = logging.getLogger(__name__)


def resolve_target_date() -> date:
    raw = os.getenv("TARGET_DATE", "")
    if raw:
        return date.fromisoformat(raw)
    return date.today() - timedelta(days=1)


def collect_all(target_date: date) -> list[Article]:
    collectors = [hackernews, techcrunch, zenn, qiita, venturebeat, a16z]
    seen: dict[str, Article] = {}

    for collector in collectors:
        try:
            for article in collector.collect(target_date):
                if article.url not in seen:
                    seen[article.url] = article
        except Exception:
            logger.warning("%s failed to collect articles", collector.__name__, exc_info=True)

    articles = list(seen.values())
    if not articles:
        logger.warning("収集した記事が0件でした")
    return articles


async def main() -> None:
    target_date = resolve_target_date()
    articles = collect_all(target_date)
    print(f"Collected {len(articles)} articles for {target_date}")
    for a in articles:
        print(f"  [{a.source}] {a.title}")

    try:
        notebook_id = await run_notebooklm(articles, target_date)
        print(f"Notebook created: https://notebooklm.google.com/notebook/{notebook_id}")
    except Exception:
        logger.error("run_notebooklm failed", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
