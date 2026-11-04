"""Shared data models passed between agents."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class MarketData:
    topic: str
    market_size_usd_bn: float
    cagr_pct: float
    history: dict[int, float]          # year -> size (USD bn)
    trends: list[str]
    forecast: dict[int, float] = field(default_factory=dict)
    yoy_growth_pct: float = 0.0


@dataclass
class Competitor:
    name: str
    share_pct: float
    price_index: float                  # 100 = market average
    strengths: list[str]
    weaknesses: list[str]


@dataclass
class CompetitorAnalysis:
    competitors: list[Competitor]
    hhi: float
    concentration: str
    leader: str
    top3_share_pct: float
    gaps: list[str]


@dataclass
class SentimentResult:
    avg_score: float                    # -1 .. +1
    label: str
    positive_pct: float
    negative_pct: float
    neutral_pct: float
    by_source: dict[str, float]
    top_positive_themes: list[str]
    top_negative_themes: list[str]
    sample_size: int


@dataclass
class Recommendation:
    priority: str                       # High / Medium / Low
    title: str
    rationale: str


@dataclass
class Report:
    topic: str
    market: MarketData
    competitors: CompetitorAnalysis
    sentiment: SentimentResult
    recommendations: list[Recommendation]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
