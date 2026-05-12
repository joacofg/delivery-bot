from __future__ import annotations

import re
from typing import List

from openai import OpenAI

from rappi_ai_analyst.config import OPENAI_API_KEY, OPENAI_MODEL
from rappi_ai_analyst.metric_catalog import METRIC_CATALOG
from rappi_ai_analyst.planner_models import PlannerEnvelope
from rappi_ai_analyst.query_models import (
    AggregationPlan,
    ComparisonPlan,
    GrowthExplanationPlan,
    MultimetricScreenPlan,
    QueryFilters,
    QueryPlan,
    RankingPlan,
    TrendPlan,
)


class QueryPlanningError(RuntimeError):
    pass


SYSTEM_PROMPT = """
You are a query planner for a Rappi operations analytics assistant.
Your only job is to convert a user's natural-language question into a structured analytics plan.
Do not answer the business question itself.

Rules:
- Use only these intents: ranking, comparison, trend, aggregation, multimetric_screen, growth_explanation.
- Prefer deterministic supported plans over broad interpretations.
- If the user asks for top/bottom zones by a metric, use ranking.
- If the user asks Wealthy vs Non Wealthy comparison in a country, use comparison with compare_dimension=zone_type.
- If the user asks for evolution over weeks for one zone, use trend.
- If the user asks average by country, use aggregation with aggregation_level=country.
- If the user asks for high X but low Y, use multimetric_screen.
- If the user asks which zones grew in orders and what explains it, use growth_explanation.
- Keep filters explicit in filters.
- Only use a country filter when the country is explicitly mentioned in the question or supplied in conversation context.
- Do not inject Bogota, Colombia, or any other geography unless the question or context actually identifies it.
- For global questions like "by country" or "top zones this week", leave filters empty unless the question explicitly narrows them.
- Use country codes when present in the question context (e.g. Mexico -> MX, Colombia -> CO).
- If a zone and city are both identifiable from question or context, include both in filters.
- Clean text fields: no trailing punctuation, commas, braces, or quotes inside city/zone names.
- Only use metrics from the allowed list.
- If the user uses a vague business concept, include the relevant heuristic_concepts entry.
""".strip()


class OpenAIQueryPlanner:
    def __init__(self, model: str = OPENAI_MODEL) -> None:
        if not OPENAI_API_KEY:
            raise QueryPlanningError("OPENAI_API_KEY is required for the query planner.")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model

    def plan(self, user_question: str, conversation_context: List[str] | None = None) -> QueryPlan:
        context_block = "\n".join(f"- {item}" for item in (conversation_context or [])) or "- none"
        metrics_block = "\n".join(f"- {metric}" for metric in sorted(METRIC_CATALOG.keys()) if metric != "Orders")

        completion = self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Allowed metrics:\n{metrics_block}\n\n"
                        f"Conversation context:\n{context_block}\n\n"
                        f"User question:\n{user_question}"
                    ),
                },
            ],
            response_format=PlannerEnvelope,
        )

        message = completion.choices[0].message
        if not message.parsed:
            raise QueryPlanningError(f"Planner refusal or parse failure: {message.refusal}")

        return self._to_query_plan(message.parsed, user_question, conversation_context or [])

    def _to_query_plan(
        self,
        envelope: PlannerEnvelope,
        user_question: str,
        conversation_context: List[str],
    ) -> QueryPlan:
        plan = envelope.plan
        filters = self._sanitize_filters(
            QueryFilters(**plan.filters.model_dump()),
            user_question=user_question,
            conversation_context=conversation_context,
        )

        if plan.intent == "ranking":
            if not plan.metric:
                raise QueryPlanningError("Ranking plan is missing metric.")
            return RankingPlan(
                metric=plan.metric,
                top_n=plan.top_n or 5,
                sort_direction=plan.sort_direction or "desc",
                filters=filters,
            )
        if plan.intent == "comparison":
            if not plan.metric:
                raise QueryPlanningError("Comparison plan is missing metric.")
            return ComparisonPlan(
                metric=plan.metric,
                compare_dimension="zone_type",
                filters=filters,
            )
        if plan.intent == "trend":
            if not plan.metric:
                raise QueryPlanningError("Trend plan is missing metric.")
            return TrendPlan(metric=plan.metric, filters=filters)
        if plan.intent == "aggregation":
            if not plan.metric:
                raise QueryPlanningError("Aggregation plan is missing metric.")
            return AggregationPlan(
                metric=plan.metric,
                aggregation_level=plan.aggregation_level or "country",
                filters=filters,
            )
        if plan.intent == "multimetric_screen":
            if not plan.high_metric or not plan.low_metric:
                raise QueryPlanningError("Multimetric screen plan is missing metrics.")
            return MultimetricScreenPlan(
                high_metric=plan.high_metric,
                low_metric=plan.low_metric,
                filters=filters,
            )
        if plan.intent == "growth_explanation":
            return GrowthExplanationPlan(
                recent_weeks=plan.recent_weeks or 5,
                top_n=plan.top_n or 10,
                filters=filters,
            )
        raise QueryPlanningError(f"Unsupported planner intent: {plan.intent}")

    def _sanitize_filters(
        self,
        filters: QueryFilters,
        user_question: str,
        conversation_context: List[str],
    ) -> QueryFilters:
        combined_text = f"{user_question} {' '.join(conversation_context)}".lower()
        question_text = user_question.lower()

        filters.country = self._clean_text(filters.country)
        filters.city = self._clean_text(filters.city)
        filters.zone = self._clean_text(filters.zone)
        filters.zone_type = self._clean_text(filters.zone_type)
        filters.prioritization = self._clean_text(filters.prioritization)

        if filters.country and not self._country_is_supported_by_text(filters.country, combined_text):
            filters.country = None
        if filters.city and filters.city.lower() not in combined_text:
            filters.city = None
        if filters.zone and filters.zone.lower() not in combined_text:
            filters.zone = None

        global_growth_query = (
            "which zones" in question_text and "orders" in question_text and "explain" in question_text
        ) or ("which zones" in question_text and "orders" in question_text and "could explain" in question_text)
        global_aggregation_query = "by country" in question_text

        if global_growth_query or global_aggregation_query:
            filters.country = None
            filters.city = None
            filters.zone = None

        return filters

    @staticmethod
    def _clean_text(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        cleaned = re.sub(r"^[\s'\"`([{]+|[\s'\"`)}\],.:;]+$", "", cleaned)
        cleaned = cleaned.replace('},', '').replace('"', '').replace("'", "").strip()
        return cleaned or None

    @staticmethod
    def _country_is_supported_by_text(country_code: str, combined_text: str) -> bool:
        aliases = {
            "MX": ["mx", "mexico"],
            "CO": ["co", "colombia"],
            "BR": ["br", "brazil", "brasil"],
            "AR": ["ar", "argentina"],
            "CL": ["cl", "chile"],
            "PE": ["pe", "peru"],
            "EC": ["ec", "ecuador"],
            "CR": ["cr", "costa rica"],
            "UY": ["uy", "uruguay"],
        }
        supported_terms = aliases.get(country_code.upper(), [country_code.lower()])
        return any(term in combined_text for term in supported_terms)
