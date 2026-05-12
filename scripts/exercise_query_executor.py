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


if __name__ == "__main__":
    executor = QueryExecutor(load_dataset(DATA_FILE))
    plans = [
        RankingPlan(metric="Lead Penetration", top_n=5),
        ComparisonPlan(metric="Perfect Orders", filters=QueryFilters(country="MX")),
        TrendPlan(metric="Gross Profit UE", filters=QueryFilters(city="Bogota", zone="Chapinero")),
        AggregationPlan(metric="Lead Penetration", aggregation_level="country"),
        MultimetricScreenPlan(
            high_metric="Lead Penetration",
            low_metric="Perfect Orders",
            filters=QueryFilters(country="MX"),
        ),
        GrowthExplanationPlan(recent_weeks=5, top_n=5),
    ]

    for plan in plans:
        result = executor.execute(plan)
        print(f"\n=== {result.title} ===")
        print(result.narrative)
        if result.heuristic_disclosure:
            print(f"Heuristic: {result.heuristic_disclosure}")
        print(result.dataframe.head(10).to_string(index=False))
