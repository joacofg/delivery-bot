from __future__ import annotations

import streamlit as st

from rappi_ai_analyst.chat_service import ChatService
from rappi_ai_analyst.config import DATA_FILE
from rappi_ai_analyst.data_loader import DataValidationError, load_dataset
from rappi_ai_analyst.insights import generate_insight_bundle
from rappi_ai_analyst.openai_planner import OpenAIQueryPlanner, QueryPlanningError
from rappi_ai_analyst.query_executor import QueryExecutionError, QueryExecutor
from rappi_ai_analyst.reporting import render_executive_report

st.set_page_config(page_title="Rappi AI Operations Analyst", layout="wide")
st.title("Rappi AI Operations Analyst")
st.caption("Local-first challenge MVP: OpenAI planner + deterministic analytics")


@st.cache_resource
def build_resources():
    bundle = load_dataset(DATA_FILE)
    planner = OpenAIQueryPlanner()
    executor = QueryExecutor(bundle)
    chat_service = ChatService(planner=planner, executor=executor)
    insight_bundle = generate_insight_bundle(bundle)
    report_markdown = render_executive_report(insight_bundle)
    return bundle, chat_service, insight_bundle, report_markdown


if "messages" not in st.session_state:
    st.session_state.messages = []
if "trace_log" not in st.session_state:
    st.session_state.trace_log = []

try:
    _, service, insight_bundle, report_markdown = build_resources()
except (DataValidationError, QueryPlanningError) as exc:
    st.error(str(exc))
    st.stop()

chat_tab, report_tab = st.tabs(["Chat Analyst", "Executive Report"])

with st.sidebar:
    st.subheader("Example prompts")
    st.markdown(
        """
- What are the top 5 zones by Lead Penetration this week?
- Compare Perfect Orders between Wealthy and Non Wealthy zones in Mexico.
- Show the evolution of Gross Profit UE in Chapinero over the last 8 weeks.
- What is the average Lead Penetration by country?
- Which zones have high Lead Penetration but low Perfect Orders in Mexico?
- Which zones have grown the most in orders over the last 5 weeks and what could explain it?
        """
    )
    if st.checkbox("Show planner traces"):
        st.json(st.session_state.trace_log)

with chat_tab:
    for index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("chart") is not None:
                st.plotly_chart(message["chart"], width="stretch", key=f"history-chart-{index}")
            if message.get("dataframe") is not None:
                st.dataframe(message["dataframe"], width="stretch", key=f"history-df-{index}")
            if message.get("heuristic_disclosure"):
                st.info(message["heuristic_disclosure"])

    question = st.chat_input("Ask an operations question...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        try:
            conversation_context = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"][-4:]
            payload, trace = service.answer(question, conversation_context=conversation_context)
        except (QueryPlanningError, QueryExecutionError, ValueError) as exc:
            with st.chat_message("assistant"):
                st.error(str(exc))
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {exc}"})
        else:
            with st.chat_message("assistant"):
                st.markdown(payload.narrative)
                if payload.chart is not None:
                    st.plotly_chart(payload.chart, width="stretch", key=f"response-chart-{len(st.session_state.messages)}")
                st.dataframe(payload.dataframe, width="stretch", key=f"response-df-{len(st.session_state.messages)}")
                if payload.heuristic_disclosure:
                    st.info(payload.heuristic_disclosure)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": payload.narrative,
                    "chart": payload.chart,
                    "dataframe": payload.dataframe,
                    "heuristic_disclosure": payload.heuristic_disclosure,
                }
            )
            st.session_state.trace_log.append(trace)

with report_tab:
    st.subheader("Executive Summary")
    st.caption("Auto-generated highlights across anomalies, deteriorating trends, benchmark gaps, correlations, and growth opportunities.")
    for item in insight_bundle.executive_summary:
        st.markdown(f"**{item.title}**")
        st.write(item.summary)
        st.caption(item.recommendation)
        st.divider()

    st.info("Growth-driver explanations and correlations are directional signals, not causal proof.")

    st.subheader("Full Markdown Report")
    st.markdown(report_markdown)

    with st.expander("Anomalies preview"):
        st.dataframe(insight_bundle.anomalies, width="stretch")
    with st.expander("Deteriorating trends preview"):
        st.dataframe(insight_bundle.deteriorations, width="stretch")
    with st.expander("Benchmark gaps preview"):
        st.dataframe(insight_bundle.benchmark_gaps, width="stretch")
    with st.expander("Correlations preview"):
        st.dataframe(insight_bundle.correlations, width="stretch")
    with st.expander("Opportunities preview"):
        st.dataframe(insight_bundle.opportunities, width="stretch")
