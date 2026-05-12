from __future__ import annotations

from rappi_ai_analyst.openai_planner import OpenAIQueryPlanner
from rappi_ai_analyst.query_models import (
    AggregationPlan,
    ComparisonPlan,
    GrowthExplanationPlan,
    MultimetricScreenPlan,
    RankingPlan,
    TrendPlan,
)


def test_planner_maps_ranking_query() -> None:
    planner = OpenAIQueryPlanner()
    plan = planner.plan("What are the top 5 zones by Lead Penetration this week?")

    assert isinstance(plan, RankingPlan)
    assert plan.metric == "Lead Penetration"
    assert plan.top_n == 5
    assert plan.filters.country is None
    assert plan.filters.city is None


def test_planner_maps_comparison_query() -> None:
    planner = OpenAIQueryPlanner()
    plan = planner.plan("Compare Perfect Orders between Wealthy and Non Wealthy zones in Mexico")

    assert isinstance(plan, ComparisonPlan)
    assert plan.metric == "Perfect Orders"
    assert plan.filters.country == "MX"


def test_planner_maps_trend_query() -> None:
    planner = OpenAIQueryPlanner()
    plan = planner.plan(
        "Show the evolution of Gross Profit UE in Chapinero over the last 8 weeks",
        conversation_context=["Chapinero is a zone in Bogota, Colombia."],
    )

    assert isinstance(plan, TrendPlan)
    assert plan.metric == "Gross Profit UE"
    assert plan.filters.zone == "Chapinero"
    assert plan.filters.city == "Bogota"
    assert plan.filters.country == "CO"


def test_planner_maps_aggregation_query() -> None:
    planner = OpenAIQueryPlanner()
    plan = planner.plan("What is the average Lead Penetration by country?")

    assert isinstance(plan, AggregationPlan)
    assert plan.metric == "Lead Penetration"
    assert plan.aggregation_level == "country"
    assert plan.filters.country is None


def test_planner_maps_multimetric_query() -> None:
    planner = OpenAIQueryPlanner()
    plan = planner.plan("Which zones have high Lead Penetration but low Perfect Orders in Mexico?")

    assert isinstance(plan, MultimetricScreenPlan)
    assert plan.high_metric == "Lead Penetration"
    assert plan.low_metric == "Perfect Orders"
    assert plan.filters.country == "MX"


def test_planner_maps_growth_query() -> None:
    planner = OpenAIQueryPlanner()
    plan = planner.plan("Which zones have grown the most in orders over the last 5 weeks and what could explain it?")

    assert isinstance(plan, GrowthExplanationPlan)
    assert plan.recent_weeks == 5
    assert plan.filters.country is None
