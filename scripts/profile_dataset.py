from __future__ import annotations

from pprint import pprint

from rappi_ai_analyst.analytics import dataset_summary, latest_metric_ranking, metric_trend
from rappi_ai_analyst.config import DATA_FILE
from rappi_ai_analyst.data_loader import load_dataset


if __name__ == "__main__":
    bundle = load_dataset(DATA_FILE)
    pprint(dataset_summary(bundle))
    print("\nTop 5 Lead Penetration (latest week)")
    print(latest_metric_ranking(bundle, "Lead Penetration").to_string(index=False))
    print("\nGross Profit UE trend for Chapinero")
    print(metric_trend(bundle, "Gross Profit UE", "Chapinero").to_string(index=False))
