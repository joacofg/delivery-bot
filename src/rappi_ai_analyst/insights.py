from __future__ import annotations

from typing import List

import pandas as pd

from rappi_ai_analyst.metric_catalog import METRIC_CATALOG
from rappi_ai_analyst.models import DatasetBundle, MetricDefinition
from rappi_ai_analyst.insight_models import InsightBundle, InsightRecord


def generate_insight_bundle(bundle: DatasetBundle) -> InsightBundle:
    anomalies = detect_anomalies(bundle)
    deteriorations = detect_deteriorating_trends(bundle)
    benchmark_gaps = detect_benchmark_gaps(bundle)
    correlations = detect_correlations(bundle)
    opportunities = detect_opportunities(bundle)

    executive_summary = build_executive_summary(
        anomalies=anomalies,
        deteriorations=deteriorations,
        benchmark_gaps=benchmark_gaps,
        correlations=correlations,
        opportunities=opportunities,
    )

    return InsightBundle(
        executive_summary=executive_summary,
        anomalies=anomalies,
        deteriorations=deteriorations,
        benchmark_gaps=benchmark_gaps,
        correlations=correlations,
        opportunities=opportunities,
    )


def detect_anomalies(bundle: DatasetBundle, threshold: float = 0.10, top_n: int = 15) -> pd.DataFrame:
    current = bundle.metrics_long[bundle.metrics_long["week_index"] == 0][["COUNTRY", "CITY", "ZONE", "METRIC", "value"]].rename(columns={"value": "current_value"})
    previous = bundle.metrics_long[bundle.metrics_long["week_index"] == 1][["COUNTRY", "CITY", "ZONE", "METRIC", "value"]].rename(columns={"value": "previous_value"})
    merged = current.merge(previous, on=["COUNTRY", "CITY", "ZONE", "METRIC"], how="inner")
    merged = merged[merged["previous_value"].notna() & (merged["previous_value"] != 0)].copy()
    merged["baseline_min_abs"] = merged["METRIC"].map(_metric_anomaly_baseline_min_abs)
    merged = merged[merged["previous_value"].abs() >= merged["baseline_min_abs"]].copy()
    merged["delta_abs"] = merged["current_value"] - merged["previous_value"]
    merged["delta_pct"] = merged["delta_abs"] / merged["previous_value"].abs()
    merged["abs_delta_pct"] = merged["delta_pct"].abs()
    filtered = merged[merged["abs_delta_pct"] >= threshold].copy()
    filtered["direction_label"] = filtered.apply(_direction_label, axis=1)
    return filtered.sort_values("abs_delta_pct", ascending=False).head(top_n).reset_index(drop=True)


def detect_deteriorating_trends(bundle: DatasetBundle, top_n: int = 15) -> pd.DataFrame:
    rows = []
    pivot = bundle.metrics_long.pivot_table(
        index=["COUNTRY", "CITY", "ZONE", "METRIC"],
        columns="week_index",
        values="value",
        aggfunc="first",
    )
    for index, row in pivot.iterrows():
        latest_window = [row.get(i) for i in [3, 2, 1, 0]]
        if any(pd.isna(v) for v in latest_window):
            continue
        metric = index[3]
        definition = METRIC_CATALOG.get(metric)
        if not definition:
            continue
        deterioration = _is_deteriorating(latest_window, definition)
        if not deterioration:
            continue
        rows.append(
            {
                "COUNTRY": index[0],
                "CITY": index[1],
                "ZONE": index[2],
                "METRIC": metric,
                "window_values": latest_window,
                "net_change": latest_window[-1] - latest_window[0],
            }
        )
    return pd.DataFrame(rows).sort_values("net_change").head(top_n).reset_index(drop=True) if rows else pd.DataFrame(columns=["COUNTRY","CITY","ZONE","METRIC","window_values","net_change"])


def detect_benchmark_gaps(bundle: DatasetBundle, top_n: int = 15) -> pd.DataFrame:
    latest = bundle.metrics_long[bundle.metrics_long["week_index"] == 0].copy()
    peer_avg = (
        latest.groupby(["COUNTRY", "ZONE_TYPE", "METRIC"], as_index=False)["value"]
        .mean()
        .rename(columns={"value": "peer_avg"})
    )
    merged = latest.merge(peer_avg, on=["COUNTRY", "ZONE_TYPE", "METRIC"], how="left")
    merged["gap_vs_peer"] = merged["value"] - merged["peer_avg"]
    merged["adverse_gap_score"] = merged.apply(_adverse_gap_score, axis=1)
    filtered = merged[merged["adverse_gap_score"] > 0].copy()
    if not filtered.empty:
        cap = filtered["adverse_gap_score"].quantile(0.95)
        filtered = filtered[filtered["adverse_gap_score"] <= cap].copy()
    return filtered.sort_values("adverse_gap_score", ascending=False).head(top_n).reset_index(drop=True)


def detect_correlations(bundle: DatasetBundle, min_abs_corr: float = 0.35) -> pd.DataFrame:
    latest = bundle.metrics_long[bundle.metrics_long["week_index"] == 0].copy()
    pivot = latest.pivot_table(index=["COUNTRY", "CITY", "ZONE"], columns="METRIC", values="value", aggfunc="first")
    corr = pivot.corr(min_periods=30)
    rows = []
    metrics = list(corr.columns)
    for i, left in enumerate(metrics):
        for right in metrics[i + 1 :]:
            value = corr.loc[left, right]
            if pd.isna(value) or abs(value) < min_abs_corr:
                continue
            rows.append({"metric_a": left, "metric_b": right, "correlation": value})
    return pd.DataFrame(rows).sort_values("correlation", key=lambda s: s.abs(), ascending=False).reset_index(drop=True) if rows else pd.DataFrame(columns=["metric_a","metric_b","correlation"])


def detect_opportunities(bundle: DatasetBundle, top_n: int = 15) -> pd.DataFrame:
    growth = _order_growth_table(bundle)
    opportunities = growth[growth["orders_growth_pct"] > 0].copy()
    opportunities = opportunities[opportunities["orders_current"] >= opportunities["orders_current"].quantile(0.5)].copy()
    opportunities["opportunity_score"] = opportunities["orders_growth_pct"] * opportunities["orders_current"]
    return opportunities.sort_values("opportunity_score", ascending=False).head(top_n).reset_index(drop=True)


def build_executive_summary(
    anomalies: pd.DataFrame,
    deteriorations: pd.DataFrame,
    benchmark_gaps: pd.DataFrame,
    correlations: pd.DataFrame,
    opportunities: pd.DataFrame,
) -> list[InsightRecord]:
    summary: List[InsightRecord] = []

    anomaly_row = _pick_executive_anomaly(anomalies)
    if anomaly_row is not None:
        row = anomaly_row
        summary.append(
            InsightRecord(
                category="anomaly",
                title=f"Sharp week-over-week move in {row['METRIC']}",
                summary=(
                    f"{row['ZONE']} ({row['CITY']}, {row['COUNTRY']}) moved {row['delta_pct']:.1%} week over week in {row['METRIC']}."
                ),
                recommendation="Review the local operational change behind the swing and confirm whether it is signal or data noise.",
                evidence=row.to_dict(),
            )
        )

    if not deteriorations.empty:
        row = deteriorations.iloc[0]
        summary.append(
            InsightRecord(
                category="deteriorating_trend",
                title=f"Sustained deterioration in {row['METRIC']}",
                summary=f"{row['ZONE']} shows a 4-week deterioration pattern in {row['METRIC']}.",
                recommendation="Escalate this zone for operator review and compare recent interventions against peer zones.",
                evidence=row.to_dict(),
            )
        )

    if not benchmark_gaps.empty:
        row = benchmark_gaps.iloc[0]
        summary.append(
            InsightRecord(
                category="benchmark_gap",
                title=f"Zone materially under peer benchmark on {row['METRIC']}",
                summary=(
                    f"{row['ZONE']} is under its {row['COUNTRY']} / {row['ZONE_TYPE']} peer average by {row['gap_vs_peer']:.3f} in {row['METRIC']}."
                ),
                recommendation="Use the best-performing peer in the same segment as the reference playbook for this zone.",
                evidence=row.to_dict(),
            )
        )

    if not correlations.empty:
        row = correlations.iloc[0]
        summary.append(
            InsightRecord(
                category="correlation",
                title=f"Strong relationship between {row['metric_a']} and {row['metric_b']}",
                summary=f"Latest-zone correlation is {row['correlation']:.2f} between {row['metric_a']} and {row['metric_b']}.",
                recommendation="Investigate whether improving one KPI can be used as an early signal for the other in weekly ops reviews.",
                evidence=row.to_dict(),
            )
        )

    if not opportunities.empty:
        row = opportunities.iloc[0]
        summary.append(
            InsightRecord(
                category="opportunity",
                title="High-growth zone worth scaling",
                summary=(
                    f"{row['ZONE']} ({row['CITY']}, {row['COUNTRY']}) grew orders by {row['orders_growth_pct']:.1%} vs its recent baseline."
                ),
                recommendation="Study the local KPI mix and replicate the strongest practices in comparable zones.",
                evidence=row.to_dict(),
            )
        )

    return summary[:5]


def _pick_executive_anomaly(anomalies: pd.DataFrame):
    if anomalies.empty:
        return None
    credible = anomalies[(anomalies["abs_delta_pct"] >= 0.15) & (anomalies["abs_delta_pct"] <= 3.0)].copy()
    if not credible.empty:
        return credible.sort_values("abs_delta_pct", ascending=False).iloc[0]
    return anomalies.iloc[0]


def _is_deteriorating(values: list[float], definition: MetricDefinition) -> bool:
    if definition.direction == "higher_is_better":
        return values[0] > values[1] > values[2] > values[3]
    if definition.direction == "lower_is_better":
        return values[0] < values[1] < values[2] < values[3]
    return False


def _direction_label(row: pd.Series) -> str:
    definition = METRIC_CATALOG.get(row["METRIC"])
    if not definition:
        return "move"
    improved = row["delta_abs"] > 0 if definition.direction == "higher_is_better" else row["delta_abs"] < 0
    return "improvement" if improved else "deterioration"


def _adverse_gap_score(row: pd.Series) -> float:
    definition = METRIC_CATALOG.get(row["METRIC"])
    if not definition or pd.isna(row["gap_vs_peer"]):
        return 0.0
    if definition.direction == "higher_is_better":
        return max(0.0, -float(row["gap_vs_peer"]))
    if definition.direction == "lower_is_better":
        return max(0.0, float(row["gap_vs_peer"]))
    return 0.0


def _metric_anomaly_baseline_min_abs(metric: str) -> float:
    definition = METRIC_CATALOG.get(metric)
    if not definition:
        return 0.05
    if definition.kind == "monetary":
        return 0.25
    if definition.kind == "count":
        return 1.0
    return 0.02


def _order_growth_table(bundle: DatasetBundle, recent_weeks: int = 5) -> pd.DataFrame:
    orders = bundle.orders_long[bundle.orders_long["METRIC"] == "Orders"].copy()
    current = orders[orders["week_index"] == 0][["COUNTRY", "CITY", "ZONE", "value"]].rename(columns={"value": "orders_current"})
    baseline = (
        orders[orders["week_index"].between(1, recent_weeks)]
        .groupby(["COUNTRY", "CITY", "ZONE"], as_index=False)["value"]
        .mean()
        .rename(columns={"value": "orders_baseline"})
    )
    merged = current.merge(baseline, on=["COUNTRY", "CITY", "ZONE"], how="inner")
    merged["orders_growth_abs"] = merged["orders_current"] - merged["orders_baseline"]
    merged["orders_growth_pct"] = merged["orders_growth_abs"] / merged["orders_baseline"]
    return merged
