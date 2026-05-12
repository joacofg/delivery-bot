from __future__ import annotations

from rappi_ai_analyst.config import DATA_FILE
from rappi_ai_analyst.data_loader import load_dataset
from rappi_ai_analyst.insights import generate_insight_bundle
from rappi_ai_analyst.reporting import render_executive_report


def test_generate_insight_bundle_has_required_sections() -> None:
    bundle = generate_insight_bundle(load_dataset(DATA_FILE))

    assert bundle.executive_summary
    assert bundle.anomalies is not None
    assert bundle.deteriorations is not None
    assert bundle.benchmark_gaps is not None
    assert bundle.correlations is not None
    assert bundle.opportunities is not None


def test_render_executive_report_contains_required_headers() -> None:
    insight_bundle = generate_insight_bundle(load_dataset(DATA_FILE))
    report = render_executive_report(insight_bundle)

    assert "# Executive Insights Report" in report
    assert "## Executive Summary" in report
    assert "## Anomalies" in report
    assert "## Deteriorating Trends" in report
    assert "## Benchmark Gaps" in report
    assert "## Correlations" in report
    assert "## Opportunities" in report
