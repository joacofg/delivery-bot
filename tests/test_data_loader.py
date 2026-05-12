from __future__ import annotations

from rappi_ai_analyst.config import DATA_FILE
from rappi_ai_analyst.data_loader import load_dataset


def test_load_dataset_builds_expected_shapes() -> None:
    bundle = load_dataset(DATA_FILE)

    assert not bundle.metrics_wide.empty
    assert not bundle.orders_wide.empty
    assert len(bundle.metrics_long) == len(bundle.metrics_wide) * 9
    assert len(bundle.orders_long) == len(bundle.orders_wide) * 9
    assert set(bundle.join_coverage["coverage_status"].unique()) == {"both", "metrics_only", "orders_only"}


def test_latest_week_has_values_for_metrics() -> None:
    bundle = load_dataset(DATA_FILE)
    latest = bundle.metrics_long[bundle.metrics_long["week_index"] == 0]

    assert latest["value"].notna().all()


def test_zone_metric_pairs_are_unique_after_deduplication() -> None:
    bundle = load_dataset(DATA_FILE)
    duplicate_zone_metric_pairs = bundle.metrics_wide.duplicated(
        subset=["COUNTRY", "CITY", "ZONE", "ZONE_TYPE", "ZONE_PRIORITIZATION", "METRIC"]
    )

    assert not duplicate_zone_metric_pairs.any()
