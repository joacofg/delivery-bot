from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd

from rappi_ai_analyst.analytics import (
    average_metric_by_country,
    compare_zone_type_performance,
    latest_metric_ranking,
    metric_definition,
    metric_trend_in_city,
    multimetric_screen,
    order_growth_with_candidate_drivers,
)
from rappi_ai_analyst.heuristics import HEURISTICS
from rappi_ai_analyst.models import DatasetBundle
from rappi_ai_analyst.query_models import (
    AggregationPlan,
    ComparisonPlan,
    GrowthExplanationPlan,
    MultimetricScreenPlan,
    QueryPlan,
    RankingPlan,
    TrendPlan,
)


@dataclass
class QueryResult:
    title: str
    dataframe: pd.DataFrame
    narrative: str
    heuristic_disclosure: Optional[str] = None
    chart_type: str = "table"
    metadata: Optional[dict[str, Any]] = None


class QueryExecutionError(RuntimeError):
    pass


class QueryExecutor:
    def __init__(self, bundle: DatasetBundle) -> None:
        self.bundle = bundle

    def execute(self, plan: QueryPlan) -> QueryResult:
        if isinstance(plan, RankingPlan):
            return self._execute_ranking(plan)
        if isinstance(plan, ComparisonPlan):
            return self._execute_comparison(plan)
        if isinstance(plan, TrendPlan):
            return self._execute_trend(plan)
        if isinstance(plan, AggregationPlan):
            return self._execute_aggregation(plan)
        if isinstance(plan, MultimetricScreenPlan):
            return self._execute_multimetric_screen(plan)
        if isinstance(plan, GrowthExplanationPlan):
            return self._execute_growth_explanation(plan)
        raise QueryExecutionError(f"Unsupported plan type: {type(plan)!r}")

    def _execute_ranking(self, plan: RankingPlan) -> QueryResult:
        dataframe = latest_metric_ranking(
            self.bundle,
            metric=plan.metric,
            top_n=plan.top_n,
            ascending=plan.sort_direction == "asc",
            country=plan.filters.country,
        )
        title = f"Top {plan.top_n} zones by {plan.metric}"
        if plan.filters.country:
            title += f" in {plan.filters.country}"
        narrative = f"Ranked zones by the latest available {plan.metric} value."
        return QueryResult(
            title=title,
            dataframe=dataframe,
            narrative=narrative,
            heuristic_disclosure=HEURISTICS["top_performers"].disclosure,
            chart_type="bar",
        )

    def _execute_comparison(self, plan: ComparisonPlan) -> QueryResult:
        if plan.compare_dimension != "zone_type" or not plan.filters.country:
            raise QueryExecutionError("Current comparison support requires zone_type comparison within a country.")
        dataframe = compare_zone_type_performance(self.bundle, metric=plan.metric, country=plan.filters.country)
        title = f"{plan.metric} comparison by zone type in {plan.filters.country}"
        narrative = f"Compared the latest {plan.metric} values between Wealthy and Non Wealthy zones in {plan.filters.country}."
        return QueryResult(title=title, dataframe=dataframe, narrative=narrative, chart_type="bar")

    def _execute_trend(self, plan: TrendPlan) -> QueryResult:
        if not plan.filters.city or not plan.filters.zone:
            raise QueryExecutionError("Trend queries currently require both city and zone.")
        dataframe = metric_trend_in_city(self.bundle, metric=plan.metric, city=plan.filters.city, zone=plan.filters.zone)
        title = f"{plan.metric} trend for {plan.filters.zone}"
        narrative = f"Showing the weekly evolution of {plan.metric} for {plan.filters.zone} in {plan.filters.city}."
        return QueryResult(
            title=title,
            dataframe=dataframe,
            narrative=narrative,
            chart_type=metric_definition(plan.metric).chart_type,
        )

    def _execute_aggregation(self, plan: AggregationPlan) -> QueryResult:
        if plan.aggregation_level != "country":
            raise QueryExecutionError("Current aggregation support is implemented for country-level averages.")
        dataframe = average_metric_by_country(self.bundle, metric=plan.metric)
        title = f"Average {plan.metric} by country"
        narrative = f"Computed the latest-week average {plan.metric} for each country."
        return QueryResult(title=title, dataframe=dataframe, narrative=narrative, chart_type="bar")

    def _execute_multimetric_screen(self, plan: MultimetricScreenPlan) -> QueryResult:
        dataframe = multimetric_screen(
            self.bundle,
            high_metric=plan.high_metric,
            low_metric=plan.low_metric,
            high_quantile=plan.high_quantile,
            low_quantile=plan.low_quantile,
            country=plan.filters.country,
        )
        title = f"High {plan.high_metric} but low {plan.low_metric}"
        narrative = (
            f"Selected zones above the {plan.high_quantile:.0%} threshold for {plan.high_metric} "
            f"and below the {plan.low_quantile:.0%} threshold for {plan.low_metric}."
        )
        return QueryResult(title=title, dataframe=dataframe, narrative=narrative, chart_type="table")

    def _execute_growth_explanation(self, plan: GrowthExplanationPlan) -> QueryResult:
        dataframe = order_growth_with_candidate_drivers(self.bundle, recent_weeks=plan.recent_weeks, top_n=plan.top_n)
        if plan.filters.country:
            dataframe = dataframe[dataframe["COUNTRY"] == plan.filters.country].reset_index(drop=True)
        title = f"Top order growth zones in the last {plan.recent_weeks} weeks"
        narrative = "Identified zones with the strongest recent order growth and summarized positive KPI co-movements that may help explain that growth."
        return QueryResult(
            title=title,
            dataframe=dataframe,
            narrative=narrative,
            heuristic_disclosure=HEURISTICS["growth_drivers"].disclosure,
            chart_type="table",
        )
