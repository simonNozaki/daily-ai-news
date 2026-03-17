from dataclasses import dataclass


@dataclass
class Article:
    url: str
    title: str
    source: str  # "hackernews" | "techcrunch" | "zenn" | "qiita"
