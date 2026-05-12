from __future__ import annotations

from rappi_ai_analyst.analytics import (
    average_metric_by_country,
    compare_zone_type_performance,
    latest_metric_ranking,
    metric_trend_in_city,
    multimetric_screen,
    order_growth_with_candidate_drivers,
)
from rappi_ai_analyst.config import DATA_FILE
from rappi_ai_analyst.data_loader import load_dataset


if __name__ == "__main__":
    bundle = load_dataset(DATA_FILE)

    print("\nAverage Lead Penetration by country")
    print(average_metric_by_country(bundle, "Lead Penetration").head(10).to_string(index=False))

    print("\nPerfect Orders by zone type in MX")
    print(compare_zone_type_performance(bundle, "Perfect Orders", country="MX").to_string(index=False))

    print("\nTop 5 zones by latest Lead Penetration")
    print(latest_metric_ranking(bundle, "Lead Penetration", top_n=5).to_string(index=False))

    print("\nGross Profit UE trend in Bogota / Chapinero")
    print(metric_trend_in_city(bundle, "Gross Profit UE", city="Bogota", zone="Chapinero").to_string(index=False))

    print("\nHigh Lead Penetration but low Perfect Orders in MX")
    print(multimetric_screen(bundle, "Lead Penetration", "Perfect Orders", country="MX").head(10).to_string(index=False))

    print("\nTop order growth zones with candidate drivers")
    print(order_growth_with_candidate_drivers(bundle, recent_weeks=5, top_n=5)[[
        "COUNTRY", "CITY", "ZONE", "orders_growth_pct", "candidate_drivers"
    ]].to_string(index=False))
