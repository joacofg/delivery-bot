# Operations AI Analyst

Local-first AI analytics application for operational data exploration and executive reporting.

This project includes two main capabilities:

1. **Conversational analytics assistant** for non-technical users
2. **Automatic executive insights report** generated from an operational dataset

The solution is intentionally optimized for a **strong local live demo** rather than production infrastructure.

---

## What the app does

### 1) Conversational analytics assistant
The Streamlit app lets a user ask natural-language operational questions such as:

- "What are the top 5 zones by Lead Penetration this week?"
- "Compare Perfect Orders between Wealthy and Non Wealthy zones in Mexico."
- "Show the evolution of Gross Profit UE in Chapinero over the last 8 weeks."
- "What is the average Lead Penetration by country?"
- "Which zones have high Lead Penetration but low Perfect Orders in Mexico?"
- "Which zones have grown the most in orders over the last 5 weeks and what could explain it?"

The app uses:
- **OpenAI** to translate the question into a structured query plan
- a **deterministic pandas analytics engine** to compute the answer
- **Streamlit + Plotly** to render narratives, tables, and charts

### 2) Automatic executive report
The app also generates a structured executive report with:
- anomalies
- deteriorating trends
- benchmark gaps
- correlations
- growth opportunities
- concise recommendations

The report is available inside the **Executive Report** tab.

---

## Why this architecture

The main design principle is:

> **Use the LLM for interpretation and explanation, not for arithmetic.**

That leads to this split:

- **OpenAI planner**
  - maps natural language to a typed query plan
  - keeps interpretation explicit and testable
- **Deterministic analytics engine**
  - performs filtering, ranking, comparisons, trends, aggregations, multimetric screens, and growth-driver summaries
- **Heuristics layer**
  - makes business assumptions explicit for vague concepts like "growth drivers" or "top performers"
- **Insights engine**
  - generates category-based findings and an executive summary
- **Streamlit presentation layer**
  - provides the local demo UI

This keeps the demo reliable and explainable.

---

## Tech stack

- Python
- Streamlit
- Pandas
- Plotly
- Pydantic
- OpenAI Python SDK
- openpyxl
- pytest

---

## Repository structure

```text
app.py
src/rappi_ai_analyst/
  analytics.py
  chat_service.py
  config.py
  data_loader.py
  heuristics.py
  insight_models.py
  insights.py
  metric_catalog.py
  models.py
  openai_planner.py
  planner_models.py
  presentation.py
  query_executor.py
  query_models.py
  reporting.py
scripts/
  exercise_analytics.py
  exercise_chat_service.py
  exercise_insights.py
  exercise_openai_planner.py
  exercise_query_executor.py
  profile_dataset.py
tests/
  test_analytics.py
  test_chat_service.py
  test_data_loader.py
  test_insights.py
  test_openai_planner.py
  test_query_executor.py
```

---

## Dataset assumptions

The data source used here is an **Excel workbook** with multiple sheets.

Used sheets:
- `RAW_INPUT_METRICS`
- `RAW_ORDERS`

Important data realities handled in code:
- the metrics and orders sheets do **not** align perfectly by zone
- the metrics sheet contains **semantic duplicates** that must be collapsed
- some metric names and dictionary descriptions are not perfectly aligned
- some metrics have scales that are **not safely interpretable as 0-1 percentages**

Because of that, the loader validates shape, normalizes the weekly columns, and exposes join coverage.

---

## Setup

### 1. Python environment
This repo was implemented and verified in a local Python 3.9 environment.

Create and activate a virtual environment if you want isolation:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python3 -m pip install --user streamlit pandas plotly pydantic openai python-dotenv openpyxl pytest
```

If you are inside a virtual environment, you can omit `--user`.

### 3. Configure OpenAI
Create a `.env` file with:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

`OPENAI_MODEL` is optional; the code defaults to `gpt-4o-mini`.

### 4. Make sure the Excel file is present
The app expects this file in the repo root:

```text
Sistema de Análisis Inteligente para Operaciones Rappi - Dummy Data (1) (1).xlsx
```

---

## Run the app

```bash
PYTHONPATH=src python3 -m streamlit run app.py --server.port 8501 --server.headless true
```

Then open:

```text
http://127.0.0.1:8501
```

---

## Run tests

Verified suite:

```bash
python3 -m pytest \
  tests/test_insights.py \
  tests/test_chat_service.py \
  tests/test_openai_planner.py \
  tests/test_query_executor.py \
  tests/test_analytics.py \
  tests/test_data_loader.py
```

---

## Useful debug / exercise scripts

### Dataset profile
```bash
PYTHONPATH=src python3 scripts/profile_dataset.py
```

### Analytics engine examples
```bash
PYTHONPATH=src python3 scripts/exercise_analytics.py
```

### Query executor examples
```bash
PYTHONPATH=src python3 scripts/exercise_query_executor.py
```

### OpenAI planner examples
```bash
PYTHONPATH=src python3 scripts/exercise_openai_planner.py
```

### Chat service smoke test
```bash
PYTHONPATH=src python3 scripts/exercise_chat_service.py
```

### Executive report generation
```bash
PYTHONPATH=src python3 scripts/exercise_insights.py
```

---

## Supported question families

The current MVP supports the following query types:

- **Ranking / filtering**
- **Wealthy vs Non Wealthy comparison by country**
- **Single-zone temporal trend**
- **Country-level average aggregation**
- **High X / low Y multimetric screening**
- **Order growth + candidate drivers**

---

## Current limitations

This project is demo-ready, but intentionally not production-ready.

### Data / methodology limitations
- anomaly detection is still somewhat noisy for `Gross Profit UE`
- the executive summary is useful, but not yet fully curated for operator trust
- correlation findings are descriptive, not causal

### Product limitations
- no authentication or persistence
- no scheduled report delivery
- no export workflow yet
- optimized for local usage, not multi-user deployment

---

## Verification notes

Key areas covered by tests:
- dataset loading and normalization
- duplicate-collapse behavior
- deterministic analytics outputs
- query execution
- OpenAI planner behavior
- chat-service orchestration
- insights/report generation

A recent verified run passed all 23 targeted tests in the suite.
