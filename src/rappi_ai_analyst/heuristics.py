from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


BusinessConcept = Literal["problematic_zones", "growth_drivers", "benchmark_peers", "top_performers"]
AnalysisIntent = Literal[
    "ranking",
    "comparison",
    "trend",
    "aggregation",
    "multimetric_screen",
    "growth_explanation",
]


@dataclass(frozen=True)
class BusinessHeuristic:
    concept: BusinessConcept
    definition: str
    disclosure: str


HEURISTICS: dict[BusinessConcept, BusinessHeuristic] = {
    "problematic_zones": BusinessHeuristic(
        concept="problematic_zones",
        definition=(
            "Zones with weak current performance relative to peers or multiple deteriorating signals, "
            "especially low Perfect Orders, negative Gross Profit UE, or adverse performance-vs-benchmark."
        ),
        disclosure=(
            "I interpret problematic zones as zones with weak current KPI levels versus comparable peers, "
            "especially low Perfect Orders, negative Gross Profit UE, or multiple deteriorating signals."
        ),
    ),
    "growth_drivers": BusinessHeuristic(
        concept="growth_drivers",
        definition=(
            "Potential growth drivers are metrics that improved alongside recent order growth and whose direction is business-positive."
        ),
        disclosure=(
            "I describe growth drivers as positive KPI co-movements associated with recent order growth, not proven causality."
        ),
    ),
    "benchmark_peers": BusinessHeuristic(
        concept="benchmark_peers",
        definition=(
            "Comparable peers are primarily zones in the same country and same zone_type; prioritization may be used as a secondary cut."
        ),
        disclosure=(
            "I compare a zone against peers in the same country and same wealth segment unless a tighter grouping is specified."
        ),
    ),
    "top_performers": BusinessHeuristic(
        concept="top_performers",
        definition="Top performers are zones with the strongest current metric values for metrics where higher is better.",
        disclosure="I rank top performers by the latest available metric value unless you specify another time window.",
    ),
}
