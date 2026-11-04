# Intelligent Market Research Analyst (Multi-Agent)

A pipeline of cooperating agents that collects market data, analyses competitors,
scores sentiment from news/social text, and produces a structured report with
prioritised recommendations.

## Architecture
```
            ┌──────────────────┐
            │   Orchestrator   │
            └───────┬──────────┘
     parallel ┌──────┼───────────┐
   MarketDataAgent  CompetitorAgent  SentimentAgent
   (size, CAGR,     (shares, HHI,    (lexicon scoring,
    forecast)        gaps)            themes by source)
              └──────┼───────────┘
                     ▼
            RecommendationAgent  (rules combining all signals)
                     ▼
            ReportWriterAgent    (Markdown + JSON)
```

## Quick start
```bash
cd market_analyst
python main.py "electric vehicles"
# -> output/electric_vehicles.md and .json
python -m pytest tests -q
```

## Data sources (`sources.py`)
| Source | Use |
|---|---|
| `MockSource` | Deterministic sample data, works offline |
| `RSSSource` | Live news headlines (Google News RSS), falls back to mock |
| `JSONFileSource` | Your own data: `{market, competitors, texts}` |

To go real, implement the `DataSource` protocol (`market`, `competitors`, `texts`)
for APIs such as NewsAPI, Reddit, X, Statista, or Crunchbase.

## Extending
- **LLM upgrade:** swap `SentimentAgent.run` or `RecommendationAgent.run` for an LLM call
  (e.g. Anthropic API) that returns the same dataclasses.
- **New agent:** subclass `agents.base.Agent`, add it to `orchestrator.py`.
- **Charts / PDF:** render `report.to_dict()` with matplotlib or a templating tool.

## Layout
```
main.py  orchestrator.py  models.py  sources.py
agents/  base, market_data, competitor, sentiment, recommender, report_writer
tests/   test_pipeline.py
```
