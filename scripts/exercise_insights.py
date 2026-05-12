from __future__ import annotations

from rappi_ai_analyst.config import DATA_FILE
from rappi_ai_analyst.data_loader import load_dataset
from rappi_ai_analyst.insights import generate_insight_bundle
from rappi_ai_analyst.reporting import render_executive_report


if __name__ == "__main__":
    bundle = load_dataset(DATA_FILE)
    insights = generate_insight_bundle(bundle)
    report = render_executive_report(insights)
    print(report)
