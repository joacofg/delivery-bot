from __future__ import annotations

from rappi_ai_analyst.config import DATA_FILE
from rappi_ai_analyst.data_loader import load_dataset
from rappi_ai_analyst.query_executor import QueryExecutor
from rappi_ai_analyst.query_models import (
    AggregationPlan,
    ComparisonPlan,
    GrowthExplanationPlan,
    MultimetricScreenPlan,
    QueryFilters,
    RankingPlan,
    TrendPlan,
)


def test_execute_ranking_plan() -> None:
    executor = QueryExecutor(load_dataset(DATA_FILE))
    result = executor.execute(RankingPlan(metric="Lead Penetration", top_n=5))

    assert result.title.startswith("Top 5 zones")
    assert len(result.dataframe) == 5
    assert result.heuristic_disclosure is not None


def test_execute_comparison_plan() -> None:
    executor = QueryExecutor(load_dataset(DATA_FILE))
    result = executor.execute(
        ComparisonPlan(metric="Perfect Orders", filters=QueryFilters(country="MX"))
    )

    assert "zone type" in result.title.lower()
    assert not result.dataframe.empty


def test_execute_trend_plan() -> None:
    executor = QueryExecutor(load_dataset(DATA_FILE))
    result = executor.execute(
        TrendPlan(metric="Gross Profit UE", filters=QueryFilters(city="Bogota", zone="Chapinero"))
    )

    assert len(result.dataframe) == 9
    assert result.chart_type == "line"


def test_execute_aggregation_plan() -> None:
    executor = QueryExecutor(load_dataset(DATA_FILE))
    result = executor.execute(AggregationPlan(metric="Lead Penetration", aggregation_level="country"))

    assert "country" in result.title.lower()
    assert "average_value" in result.dataframe.columns


def test_execute_multimetric_screen_plan() -> None:
    executor = QueryExecutor(load_dataset(DATA_FILE))
    result = executor.execute(
        MultimetricScreenPlan(
            high_metric="Lead Penetration",
            low_metric="Perfect Orders",
            filters=QueryFilters(country="MX"),
        )
    )

    assert "high" in result.title.lower()
    assert {"high_metric_value", "low_metric_value"}.issubset(result.dataframe.columns)


def test_execute_growth_explanation_plan() -> None:
    executor = QueryExecutor(load_dataset(DATA_FILE))
    result = executor.execute(GrowthExplanationPlan(recent_weeks=5, top_n=5))

    assert len(result.dataframe) <= 5
    assert result.heuristic_disclosure is not None
