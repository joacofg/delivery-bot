# Demo Script

Suggested 20-minute live demo flow for the Rappi AI Engineer challenge.

---

## 1. Context and approach (2-3 min)

Open with this framing:

- The challenge asks for two things:
  1. a natural-language analytics assistant
  2. an automatic executive insights system
- I optimized for **reliability in a live demo**.
- The key architecture choice was:
  - **OpenAI interprets the question**
  - **deterministic pandas code computes the answer**
- That avoids hallucinated arithmetic and keeps the system explainable.

Short version:

> “I treated this as an AI orchestration problem, not as an ‘ask the LLM to reason over a spreadsheet’ problem.”

---

## 2. Show the app entry point (1 min)

Open the Streamlit app and point out:

- **Chat Analyst** tab
- **Executive Report** tab
- example prompts on the left

Say:

> “The same normalized data layer powers both the conversational bot and the report engine.”

---

## 3. Demo the chatbot (8-10 min)

Use at least 5 questions from different categories.

### Q1 — Ranking / filtering
**Prompt:**

> What are the top 5 zones by Lead Penetration this week?

What to highlight:
- returns a ranked table
- uses deterministic latest-week values
- planner converts question into a structured query plan

### Q2 — Comparison
**Prompt:**

> Compare Perfect Orders between Wealthy and Non Wealthy zones in Mexico.

What to highlight:
- comparison by segment
- country filter applied correctly
- chart and table support operator interpretation

### Q3 — Trend
**Prompt:**

> Show the evolution of Gross Profit UE in Chapinero over the last 8 weeks.

What to highlight:
- time-series chart
- trend rendering
- planner uses city/zone context

### Q4 — Aggregation
**Prompt:**

> What is the average Lead Penetration by country?

What to highlight:
- country-level aggregation
- clear chart output
- simple executive-style answer

### Q5 — Multivariable analysis
**Prompt:**

> Which zones have high Lead Penetration but low Perfect Orders in Mexico?

What to highlight:
- quantile-based screening
- more advanced than plain lookup
- useful for identifying tradeoffs or operational imbalance

### Q6 — Growth explanation
**Prompt:**

> Which zones have grown the most in orders over the last 5 weeks and what could explain it?

What to highlight:
- growth is based on deterministic order baselines
- drivers are explicitly framed as **associated KPI co-movements**, not causality
- this is a business-safe interpretation

---

## 4. Show the executive report (4-5 min)

Go to **Executive Report**.

Walk through:
- Executive Summary
- one anomaly / deterioration
- one benchmark gap
- one correlation
- one opportunity

Suggested framing:

> “The report is meant to replace repetitive weekly scanning with a structured first draft for an operator or SP&A analyst.”

What to mention:
- findings are categorized
- each summary item includes a recommendation
- the full markdown report is visible in-app
- the raw tables are available underneath for drill-down

---

## 5. Technical decisions (3-4 min)

Three good points to emphasize:

### A. LLM only for planning, not math
Why:
- more reliable
- easier to test
- less hallucination risk

### B. Explicit business heuristics
Why:
- challenge expects business context understanding
- vague terms should not be hidden magic

Example:
- growth drivers are described as associated positive KPI co-movements

### C. Local-first Streamlit build
Why:
- fastest path to a strong live demo
- no unnecessary deployment complexity
- good enough UI surface for charts, chat, and report review

---

## 6. Limitations and next steps (1-2 min)

Be direct here.

Suggested points:

- anomaly ranking still needs more business calibration, especially for `Gross Profit UE`
- report curation could be stronger with more time
- no export or scheduled delivery yet
- memory is optimized for short demo conversations, not long analyst sessions
- next iteration would improve:
  - report quality scoring
  - exports
  - UX polish
  - deployment and persistence

---

## 7. Q&A backup answers

### Why not a SQL agent?
Because the challenge is small enough that a deterministic analytics layer is faster, safer, and easier to explain than adding a database+SQL agent abstraction.

### Why Streamlit?
Because the goal was a strong local demo under time pressure, not a production frontend architecture.

### Why OpenAI?
Because structured planning with typed outputs is strong and easy to validate.

### Are the insights causal?
No. Correlations and growth-driver explanations are intentionally presented as associated signals, not causality.

### Biggest technical risk you found?
Dataset quality and semantics:
- duplicate metric rows
- imperfect joins between metrics and orders
- metric scales that are not consistently 0-1

---

## Ideal closing line

> “The main thing I wanted to prove is that this can be built as a trustworthy AI workflow: the model interprets the question, but the numbers come from deterministic logic that operators can trust and inspect.”
