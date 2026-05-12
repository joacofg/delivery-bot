from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

AnalysisIntent = Literal[
    "ranking",
    "comparison",
    "trend",
    "aggregation",
    "multimetric_screen",
    "growth_explanation",
]
SortDirection = Literal["asc", "desc"]
AggregationLevel = Literal["country", "city", "zone_type"]


class QueryFilters(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None
    zone: Optional[str] = None
    zone_type: Optional[str] = None
    prioritization: Optional[str] = None


class RankingPlan(BaseModel):
    intent: Literal["ranking"] = "ranking"
    metric: str
    top_n: int = 5
    sort_direction: SortDirection = "desc"
    filters: QueryFilters = Field(default_factory=QueryFilters)


class ComparisonPlan(BaseModel):
    intent: Literal["comparison"] = "comparison"
    metric: str
    compare_dimension: Literal["zone_type"] = "zone_type"
    filters: QueryFilters = Field(default_factory=QueryFilters)


class TrendPlan(BaseModel):
    intent: Literal["trend"] = "trend"
    metric: str
    filters: QueryFilters


class AggregationPlan(BaseModel):
    intent: Literal["aggregation"] = "aggregation"
    metric: str
    aggregation_level: AggregationLevel
    filters: QueryFilters = Field(default_factory=QueryFilters)


class MultimetricScreenPlan(BaseModel):
    intent: Literal["multimetric_screen"] = "multimetric_screen"
    high_metric: str
    low_metric: str
    high_quantile: float = 0.75
    low_quantile: float = 0.25
    filters: QueryFilters = Field(default_factory=QueryFilters)


class GrowthExplanationPlan(BaseModel):
    intent: Literal["growth_explanation"] = "growth_explanation"
    recent_weeks: int = 5
    top_n: int = 10
    filters: QueryFilters = Field(default_factory=QueryFilters)


QueryPlan = Union[
    RankingPlan,
    ComparisonPlan,
    TrendPlan,
    AggregationPlan,
    MultimetricScreenPlan,
    GrowthExplanationPlan,
]
