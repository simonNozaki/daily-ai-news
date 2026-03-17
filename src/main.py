import asyncio

from dotenv import load_dotenv

from .collectors import Article
from .collectors import hackernews, techcrunch, zenn, qiita
from .notebooklm_client import run_notebooklm

load_dotenv()


def collect_all() -> list[Article]:
    collectors = [hackernews, techcrunch, zenn, qiita]
    seen: dict[str, Article] = {}

    for collector in collectors:
        try:
            for article in collector.collect():
                if article.url not in seen:
                    seen[article.url] = article
        except Exception as e:
            print(f"[WARN] {collector.__name__} failed: {e}")

    return list(seen.values())


async def main() -> None:
    articles = collect_all()
    print(f"Collected {len(articles)} articles")
    for a in articles:
        print(f"  [{a.source}] {a.title}")

    notebook_id = await run_notebooklm(articles)
    print(f"Notebook created: https://notebooklm.google.com/notebook/{notebook_id}")


if __name__ == "__main__":
    asyncio.run(main())
