"""Data sources. Swap these for real APIs (Statista, NewsAPI, Reddit, X, etc.).

Every source returns plain dicts, so agents don't care where data came from.
- MockSource: deterministic sample data (works offline, used by tests)
- JSONFileSource: load your own data from a JSON file
- RSSSource: pull live news headlines from RSS feeds (needs network)
"""
from __future__ import annotations
import hashlib, json, random, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Protocol


class DataSource(Protocol):
    def market(self, topic: str) -> dict: ...
    def competitors(self, topic: str) -> list[dict]: ...
    def texts(self, topic: str) -> list[dict]: ...   # [{"source":..., "text":...}]


class MockSource:
    POS = ["love the quality", "great value and reliable", "impressive innovation",
           "excellent customer support", "fast growth and strong demand",
           "easy to use and affordable"]
    NEG = ["too expensive", "poor customer support", "unreliable and slow delivery",
           "disappointed by quality", "confusing pricing", "weak integration options"]
    NEU = ["announced a new release", "market report published", "company expands to new region"]

    def _rng(self, topic: str) -> random.Random:
        return random.Random(int(hashlib.md5(topic.lower().encode()).hexdigest(), 16) % 2**32)

    def market(self, topic: str) -> dict:
        r = self._rng(topic)
        size = round(r.uniform(8, 120), 1)
        cagr = round(r.uniform(2, 22), 1)
        year = 2025
        history = {}
        for i in range(5, 0, -1):
            history[year - i + 1] = round(size / (1 + cagr / 100) ** (i - 1), 2)
        return {"market_size_usd_bn": history[year], "cagr_pct": cagr, "history": history,
                "trends": [f"Rising adoption of AI in {topic}",
                           f"Shift toward subscription pricing in {topic}",
                           "Growing regulatory and sustainability scrutiny",
                           "Consolidation through M&A"]}

    def competitors(self, topic: str) -> list[dict]:
        r = self._rng(topic + "c")
        names = ["Alpha Corp", "Beta Systems", "Gamma Labs", "Delta Co", "Epsilon Inc"]
        raw = [r.uniform(5, 40) for _ in names]
        scale = 85 / sum(raw)
        pool_s = ["strong brand", "wide distribution", "low price", "innovative product",
                  "great support", "deep integrations"]
        pool_w = ["high price", "slow innovation", "limited regions", "weak support",
                  "poor UX", "narrow portfolio"]
        return [{"name": n, "share_pct": round(v * scale, 1),
                 "price_index": round(r.uniform(75, 130)),
                 "strengths": r.sample(pool_s, 2), "weaknesses": r.sample(pool_w, 2)}
                for n, v in zip(names, raw)]

    def texts(self, topic: str) -> list[dict]:
        r = self._rng(topic + "t")
        out = []
        for src in ("news", "twitter", "reddit"):
            for _ in range(14):
                pool = r.choices([self.POS, self.NEG, self.NEU], weights=[45, 35, 20])[0]
                out.append({"source": src, "text": f"{topic}: {r.choice(pool)}"})
        return out


class JSONFileSource:
    """Expected keys: market{...}, competitors[...], texts[...]"""
    def __init__(self, path: str):
        self.data = json.loads(Path(path).read_text())
    def market(self, topic): return self.data["market"]
    def competitors(self, topic): return self.data["competitors"]
    def texts(self, topic): return self.data["texts"]


class RSSSource(MockSource):
    """Live news via Google News RSS for the `texts` feed; other data stays mock
    until you connect a market-data API."""
    def texts(self, topic: str) -> list[dict]:
        url = ("https://news.google.com/rss/search?q=" + urllib.parse.quote(topic))
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                root = ET.fromstring(resp.read())
            items = [{"source": "news", "text": (i.findtext("title") or "")}
                     for i in root.iter("item")]
            return items[:50] or super().texts(topic)
        except Exception:
            return super().texts(topic)   # graceful fallback
