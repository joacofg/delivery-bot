from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd

from rappi_ai_analyst.metric_catalog import METRIC_CATALOG
from rappi_ai_analyst.models import DatasetBundle, MetricDefinition

LATEST_WEEK = 0


def dataset_summary(bundle: DatasetBundle) -> dict[str, Any]:
    coverage = bundle.join_coverage["coverage_status"].value_counts().to_dict()
    return {
        "countries": int(bundle.metrics_wide["COUNTRY"].nunique()),
        "cities": int(bundle.metrics_wide["CITY"].nunique()),
        "zones_with_metrics": int(bundle.metrics_wide["ZONE"].nunique()),
        "zones_with_orders": int(bundle.orders_wide["ZONE"].nunique()),
        "metrics": sorted(bundle.metrics_wide["METRIC"].unique().tolist()),
        "metric_catalog": {name: asdict(defn) for name, defn in METRIC_CATALOG.items()},
        "join_coverage": coverage,
        "duplicate_rows_removed": {
            "metrics": 12573 - len(bundle.metrics_wide),
            "orders": 1242 - len(bundle.orders_wide),
        },
    }


def latest_metric_ranking(
    bundle: DatasetBundle,
    metric: str,
    top_n: int = 5,
    ascending: bool = False,
    country: str | None = None,
) -> pd.DataFrame:
    filtered = _latest_metric_frame(bundle, metric)
    if country:
        filtered = filtered[filtered["COUNTRY"] == country]
    return (
        filtered.sort_values("value", ascending=ascending)
        .head(top_n)
        [["COUNTRY", "CITY", "ZONE", "ZONE_TYPE", "ZONE_PRIORITIZATION", "value"]]
        .reset_index(drop=True)
    )


def average_metric_by_country(bundle: DatasetBundle, metric: str) -> pd.DataFrame:
    filtered = _latest_metric_frame(bundle, metric)
    return (
        filtered.groupby("COUNTRY", as_index=False)["value"]
        .mean()
        .rename(columns={"value": "average_value"})
        .sort_values("average_value", ascending=False)
        .reset_index(drop=True)
    )


def compare_zone_type_performance(bundle: DatasetBundle, metric: str, country: str) -> pd.DataFrame:
    filtered = _latest_metric_frame(bundle, metric)
    filtered = filtered[filtered["COUNTRY"] == country]
    return (
        filtered.groupby("ZONE_TYPE", as_index=False)["value"]
        .agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={"mean": "avg_value", "median": "median_value", "count": "zone_count"})
        .sort_values("avg_value", ascending=False)
        .reset_index(drop=True)
    )


def metric_trend(bundle: DatasetBundle, metric: str, zone: str) -> pd.DataFrame:
    filtered = bundle.metrics_long[(bundle.metrics_long["METRIC"] == metric) & (bundle.metrics_long["ZONE"] == zone)].copy()
    return filtered.sort_values("week_index")[["COUNTRY", "CITY", "ZONE", "week_label", "week_index", "value"]].reset_index(drop=True)


def metric_trend_in_city(bundle: DatasetBundle, metric: str, city: str, zone: str) -> pd.DataFrame:
    filtered = bundle.metrics_long[
        (bundle.metrics_long["METRIC"] == metric) & (bundle.metrics_long["CITY"] == city) & (bundle.metrics_long["ZONE"] == zone)
    ].copy()
    return filtered.sort_values("week_index")[["COUNTRY", "CITY", "ZONE", "week_label", "week_index", "value"]].reset_index(drop=True)


def orders_trend(bundle: DatasetBundle, zone: str) -> pd.DataFrame:
    filtered = bundle.orders_long[(bundle.orders_long["METRIC"] == "Orders") & (bundle.orders_long["ZONE"] == zone)].copy()
    return filtered.sort_values("week_index")[["COUNTRY", "CITY", "ZONE", "week_label", "week_index", "value"]].reset_index(drop=True)


def multimetric_screen(
    bundle: DatasetBundle,
    high_metric: str,
    low_metric: str,
    high_quantile: float = 0.75,
    low_quantile: float = 0.25,
    country: str | None = None,
) -> pd.DataFrame:
    left = _latest_metric_frame(bundle, high_metric)
    right = _latest_metric_frame(bundle, low_metric)
    if country:
        left = left[left["COUNTRY"] == country]
        right = right[right["COUNTRY"] == country]

    merged = left.merge(
        right[["COUNTRY", "CITY", "ZONE", "value"]].rename(columns={"value": "low_metric_value"}),
        on=["COUNTRY", "CITY", "ZONE"],
        how="inner",
    ).rename(columns={"value": "high_metric_value"})

    high_threshold = merged["high_metric_value"].quantile(high_quantile)
    low_threshold = merged["low_metric_value"].quantile(low_quantile)

    filtered = merged[
        (merged["high_metric_value"] >= high_threshold)
        & (merged["low_metric_value"] <= low_threshold)
    ].copy()
    filtered["high_metric"] = high_metric
    filtered["low_metric"] = low_metric
    filtered["high_threshold"] = high_threshold
    filtered["low_threshold"] = low_threshold
    return filtered.sort_values(["high_metric_value", "low_metric_value"], ascending=[False, True]).reset_index(drop=True)


def order_growth_with_candidate_drivers(bundle: DatasetBundle, recent_weeks: int = 5, top_n: int = 10) -> pd.DataFrame:
    order_growth = _order_growth_table(bundle, recent_weeks=recent_weeks)
    latest_metrics = _latest_metrics_pivot(bundle)
    driver_deltas = _metric_delta_pivot(bundle, recent_weeks=recent_weeks)

    merged = order_growth.merge(latest_metrics, on=["COUNTRY", "CITY", "ZONE"], how="left")
    merged = merged.merge(driver_deltas, on=["COUNTRY", "CITY", "ZONE"], how="left")

    top_growth = merged.sort_values("orders_growth_pct", ascending=False).head(top_n).copy()
    top_growth["candidate_drivers"] = top_growth.apply(_summarize_candidate_drivers, axis=1)
    return top_growth.reset_index(drop=True)


def _latest_metric_frame(bundle: DatasetBundle, metric: str) -> pd.DataFrame:
    filtered = bundle.metrics_long[(bundle.metrics_long["METRIC"] == metric) & (bundle.metrics_long["week_index"] == LATEST_WEEK)].copy()
    return filtered.reset_index(drop=True)


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


def _latest_metrics_pivot(bundle: DatasetBundle) -> pd.DataFrame:
    latest = bundle.metrics_long[bundle.metrics_long["week_index"] == 0].copy()
    pivot = latest.pivot_table(index=["COUNTRY", "CITY", "ZONE"], columns="METRIC", values="value", aggfunc="first").reset_index()
    pivot.columns.name = None
    return pivot


def _metric_delta_pivot(bundle: DatasetBundle, recent_weeks: int = 5) -> pd.DataFrame:
    metrics = bundle.metrics_long.copy()
    current = metrics[metrics["week_index"] == 0][["COUNTRY", "CITY", "ZONE", "METRIC", "value"]].rename(columns={"value": "current_value"})
    baseline = (
        metrics[metrics["week_index"].between(1, recent_weeks)]
        .groupby(["COUNTRY", "CITY", "ZONE", "METRIC"], as_index=False)["value"]
        .mean()
        .rename(columns={"value": "baseline_value"})
    )
    delta = current.merge(baseline, on=["COUNTRY", "CITY", "ZONE", "METRIC"], how="inner")
    delta["delta_vs_recent_avg"] = delta["current_value"] - delta["baseline_value"]
    pivot = delta.pivot_table(
        index=["COUNTRY", "CITY", "ZONE"],
        columns="METRIC",
        values="delta_vs_recent_avg",
        aggfunc="first",
    ).reset_index()
    pivot.columns = [
        column if isinstance(column, str) and column in {"COUNTRY", "CITY", "ZONE"} else f"delta::{column}"
        for column in pivot.columns
    ]
    return pivot


def _summarize_candidate_drivers(row: pd.Series) -> str:
    candidates: list[tuple[str, float]] = []
    for metric_name, definition in METRIC_CATALOG.items():
        if metric_name == "Orders":
            continue
        column = f"delta::{metric_name}"
        if column not in row or pd.isna(row[column]):
            continue
        value = float(row[column])
        if definition.direction == "higher_is_better" and value > 0:
            candidates.append((metric_name, value))
        elif definition.direction == "lower_is_better" and value < 0:
            candidates.append((metric_name, abs(value)))
    if not candidates:
        return "No clear positive metric co-movements found."
    top = sorted(candidates, key=lambda item: item[1], reverse=True)[:3]
    return "; ".join(f"{name} improved by {magnitude:.3f} vs recent average" for name, magnitude in top)


def metric_definition(metric: str) -> MetricDefinition:
    return METRIC_CATALOG[metric]
