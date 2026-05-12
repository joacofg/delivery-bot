from __future__ import annotations

from rappi_ai_analyst.chat_service import ChatService
from rappi_ai_analyst.config import DATA_FILE
from rappi_ai_analyst.data_loader import load_dataset
from rappi_ai_analyst.openai_planner import OpenAIQueryPlanner
from rappi_ai_analyst.query_executor import QueryExecutor


if __name__ == "__main__":
    service = ChatService(
        planner=OpenAIQueryPlanner(),
        executor=QueryExecutor(load_dataset(DATA_FILE)),
    )
    payload, trace = service.answer("What is the average Lead Penetration by country?")
    print(payload.title)
    print(payload.narrative)
    print(payload.dataframe.head(10).to_string(index=False))
    print(trace)
