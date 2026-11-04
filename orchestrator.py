"""Runs collection agents in parallel, then recommendation + report agents in sequence."""
from concurrent.futures import ThreadPoolExecutor
from agents import (MarketDataAgent, CompetitorAgent, SentimentAgent,
                    RecommendationAgent, ReportWriterAgent)


def run_pipeline(topic: str, source):
    ctx = {"topic": topic}
    collectors = {"market": MarketDataAgent(source), "competitors": CompetitorAgent(source),
                  "sentiment": SentimentAgent(source)}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {k: pool.submit(a, ctx) for k, a in collectors.items()}
        for k, f in futures.items():
            ctx[k] = f.result()
    ctx["recommendations"] = RecommendationAgent()(ctx)
    return ReportWriterAgent()(ctx)
