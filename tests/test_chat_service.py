from __future__ import annotations

from rappi_ai_analyst.chat_service import ChatService
from rappi_ai_analyst.config import DATA_FILE
from rappi_ai_analyst.data_loader import load_dataset
from rappi_ai_analyst.openai_planner import OpenAIQueryPlanner
from rappi_ai_analyst.query_executor import QueryExecutor


def test_chat_service_answers_with_trace() -> None:
    service = ChatService(
        planner=OpenAIQueryPlanner(),
        executor=QueryExecutor(load_dataset(DATA_FILE)),
    )

    payload, trace = service.answer(
        "What is the average Lead Penetration by country?",
        conversation_context=[],
    )

    assert payload.title
    assert not payload.dataframe.empty
    assert trace["question"]
    assert trace["row_count"] > 0
