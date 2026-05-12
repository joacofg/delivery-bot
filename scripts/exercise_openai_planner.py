from __future__ import annotations

from rappi_ai_analyst.openai_planner import OpenAIQueryPlanner


if __name__ == "__main__":
    planner = OpenAIQueryPlanner()
    prompts = [
        "What are the top 5 zones by Lead Penetration this week?",
        "Compare Perfect Orders between Wealthy and Non Wealthy zones in Mexico.",
        "Show the evolution of Gross Profit UE in Chapinero over the last 8 weeks.",
        "What is the average Lead Penetration by country?",
        "Which zones have high Lead Penetration but low Perfect Orders in Mexico?",
        "Which zones have grown the most in orders over the last 5 weeks and what could explain it?",
    ]

    for prompt in prompts:
        plan = planner.plan(prompt, conversation_context=["Chapinero is a zone in Bogota, Colombia."])
        print(f"\nQUESTION: {prompt}")
        print(plan.model_dump())
