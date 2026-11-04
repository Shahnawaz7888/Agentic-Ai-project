"""Usage:
  python main.py "electric vehicles"                    # sample data
  python main.py "electric vehicles" --source rss       # live news headlines
  python main.py "my market" --source json --data my.json
"""
import argparse, json, logging
from pathlib import Path
from orchestrator import run_pipeline
from agents.report_writer import ReportWriterAgent
from sources import MockSource, RSSSource, JSONFileSource


def main():
    p = argparse.ArgumentParser(description="Intelligent Market Research Analyst")
    p.add_argument("topic")
    p.add_argument("--source", choices=["mock", "rss", "json"], default="mock")
    p.add_argument("--data", help="JSON file (with --source json)")
    p.add_argument("--out", default="output")
    a = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    src = {"mock": MockSource, "rss": RSSSource}.get(a.source, lambda: JSONFileSource(a.data))()
    report = run_pipeline(a.topic, src)

    out = Path(a.out); out.mkdir(exist_ok=True)
    slug = a.topic.lower().replace(" ", "_")
    (out / f"{slug}.md").write_text(ReportWriterAgent.to_markdown(report))
    (out / f"{slug}.json").write_text(json.dumps(report.to_dict(), indent=2))
    print(f"\nReport saved to {out}/{slug}.md and .json")


if __name__ == "__main__":
    main()
