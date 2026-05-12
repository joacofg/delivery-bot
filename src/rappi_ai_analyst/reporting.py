from __future__ import annotations

from typing import Iterable

from rappi_ai_analyst.insight_models import InsightBundle, InsightRecord


def render_executive_report(bundle: InsightBundle) -> str:
    lines: list[str] = []
    lines.append("# Executive Insights Report")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    for item in bundle.executive_summary:
        lines.extend(_render_summary_item(item))
        lines.append("")

    lines.append("## Anomalies")
    lines.append("")
    lines.append(_render_dataframe_preview(bundle.anomalies, ["COUNTRY", "CITY", "ZONE", "METRIC", "delta_pct", "direction_label"]))
    lines.append("")

    lines.append("## Deteriorating Trends")
    lines.append("")
    lines.append(_render_dataframe_preview(bundle.deteriorations, ["COUNTRY", "CITY", "ZONE", "METRIC", "net_change"]))
    lines.append("")

    lines.append("## Benchmark Gaps")
    lines.append("")
    lines.append(_render_dataframe_preview(bundle.benchmark_gaps, ["COUNTRY", "CITY", "ZONE", "ZONE_TYPE", "METRIC", "gap_vs_peer"]))
    lines.append("")

    lines.append("## Correlations")
    lines.append("")
    lines.append(_render_dataframe_preview(bundle.correlations, ["metric_a", "metric_b", "correlation"]))
    lines.append("")

    lines.append("## Opportunities")
    lines.append("")
    lines.append(_render_dataframe_preview(bundle.opportunities, ["COUNTRY", "CITY", "ZONE", "orders_growth_pct", "opportunity_score"]))
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def _render_summary_item(item: InsightRecord) -> Iterable[str]:
    yield f"### {item.title}"
    yield f"- Category: `{item.category}`"
    yield f"- Finding: {item.summary}"
    yield f"- Recommendation: {item.recommendation}"


def _render_dataframe_preview(df, columns: list[str], top_n: int = 10) -> str:
    if df.empty:
        return "No findings."
    preview = df[columns].head(top_n).copy().fillna("")
    headers = [str(column) for column in preview.columns.tolist()]
    rows = [[str(value) for value in row] for row in preview.to_numpy().tolist()]

    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    header_row = "| " + " | ".join(headers) + " |"
    body_rows = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_row, separator] + body_rows)
