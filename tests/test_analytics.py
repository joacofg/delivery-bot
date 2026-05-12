from __future__ import annotations

from rappi_ai_analyst.analytics import (
    average_metric_by_country,
    compare_zone_type_performance,
    latest_metric_ranking,
    metric_trend_in_city,
    multimetric_screen,
    order_growth_with_candidate_drivers,
)
from rappi_ai_analyst.config import DATA_FILE
from rappi_ai_analyst.data_loader import load_dataset


def test_average_metric_by_country_returns_expected_columns() -> None:
    bundle = load_dataset(DATA_FILE)
    result = average_metric_by_country(bundle, "Lead Penetration")

    assert list(result.columns) == ["COUNTRY", "average_value"]
    assert not result.empty


def test_compare_zone_type_performance_returns_wealth_segments() -> None:
    bundle = load_dataset(DATA_FILE)
    result = compare_zone_type_performance(bundle, "Perfect Orders", country="MX")

    assert set(result["ZONE_TYPE"]) <= {"Wealthy", "Non Wealthy"}
    assert {"avg_value", "median_value", "zone_count"}.issubset(result.columns)


def test_metric_trend_in_city_returns_nine_weeks() -> None:
    bundle = load_dataset(DATA_FILE)
    result = metric_trend_in_city(bundle, "Gross Profit UE", city="Bogota", zone="Chapinero")

    assert len(result) == 9
    assert result["week_index"].tolist() == list(range(0, 9))


def test_multimetric_screen_returns_threshold_metadata() -> None:
    bundle = load_dataset(DATA_FILE)
    result = multimetric_screen(bundle, "Lead Penetration", "Perfect Orders", country="MX")

    assert {"high_metric", "low_metric", "high_threshold", "low_threshold"}.issubset(result.columns)


def test_order_growth_with_candidate_drivers_returns_growth_features() -> None:
    bundle = load_dataset(DATA_FILE)
    result = order_growth_with_candidate_drivers(bundle, recent_weeks=5, top_n=5)

    assert len(result) <= 5
    assert {"orders_growth_abs", "orders_growth_pct", "candidate_drivers"}.issubset(result.columns)
