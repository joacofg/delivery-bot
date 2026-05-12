from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel

from rappi_ai_analyst.query_models import QueryFilters


class PlannedQuery(BaseModel):
    intent: Literal[
        "ranking",
        "comparison",
        "trend",
        "aggregation",
        "multimetric_screen",
        "growth_explanation",
    ]
    metric: Optional[str] = None
    high_metric: Optional[str] = None
    low_metric: Optional[str] = None
    top_n: Optional[int] = None
    recent_weeks: Optional[int] = None
    compare_dimension: Optional[str] = None
    aggregation_level: Optional[str] = None
    sort_direction: Optional[Literal["asc", "desc"]] = None
    filters: QueryFilters
    heuristic_concepts: List[str] = []
    reasoning: str


class PlannerEnvelope(BaseModel):
    plan: PlannedQuery
