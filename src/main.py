import asyncio
import os
from datetime import date, timedelta

from dotenv import load_dotenv

from .collectors import Article
from .collectors import hackernews, techcrunch, zenn, qiita
from .notebooklm_client import run_notebooklm

load_dotenv()


def resolve_target_date() -> date:
    raw = os.getenv("TARGET_DATE", "")
    if raw:
        return date.fromisoformat(raw)
    return date.today() - timedelta(days=1)


def collect_all(target_date: date) -> list[Article]:
    collectors = [hackernews, techcrunch, zenn, qiita]
    seen: dict[str, Article] = {}

    for collector in collectors:
        try:
            for article in collector.collect(target_date):
                if article.url not in seen:
                    seen[article.url] = article
        except Exception as e:
            print(f"[WARN] {collector.__name__} failed: {e}")

    return list(seen.values())


async def main() -> None:
    target_date = resolve_target_date()
    articles = collect_all(target_date)
    print(f"Collected {len(articles)} articles for {target_date}")
    for a in articles:
        print(f"  [{a.source}] {a.title}")

    notebook_id = await run_notebooklm(articles, target_date)
    print(f"Notebook created: https://notebooklm.google.com/notebook/{notebook_id}")


if __name__ == "__main__":
    asyncio.run(main())
