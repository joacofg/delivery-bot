from __future__ import annotations

from dataclasses import asdict
from typing import Any

from rappi_ai_analyst.openai_planner import OpenAIQueryPlanner
from rappi_ai_analyst.presentation import RenderPayload, build_render_payload
from rappi_ai_analyst.query_executor import QueryExecutor


class ChatService:
    def __init__(self, planner: OpenAIQueryPlanner, executor: QueryExecutor) -> None:
        self.planner = planner
        self.executor = executor

    def answer(self, question: str, conversation_context: list[str] | None = None) -> tuple[RenderPayload, dict[str, Any]]:
        plan = self.planner.plan(question, conversation_context=conversation_context or [])
        result = self.executor.execute(plan)
        payload = build_render_payload(
            title=result.title,
            dataframe=result.dataframe,
            chart_type=result.chart_type,
            narrative=result.narrative,
            heuristic_disclosure=result.heuristic_disclosure,
            metadata=result.metadata,
        )
        trace = {
            "question": question,
            "plan": plan.model_dump(),
            "result_title": result.title,
            "row_count": len(result.dataframe),
        }
        return payload, trace
