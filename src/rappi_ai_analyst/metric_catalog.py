from __future__ import annotations

from rappi_ai_analyst.models import MetricDefinition


METRIC_CATALOG: dict[str, MetricDefinition] = {
    "% PRO Users Who Breakeven": MetricDefinition(
        name="% PRO Users Who Breakeven",
        kind="ratio",
        direction="higher_is_better",
        description="Share of Pro users whose generated value covers membership cost.",
    ),
    "% Restaurants Sessions With Optimal Assortment": MetricDefinition(
        name="% Restaurants Sessions With Optimal Assortment",
        kind="ratio",
        direction="higher_is_better",
        description="Share of sessions with a sufficient restaurant assortment.",
    ),
    "Gross Profit UE": MetricDefinition(
        name="Gross Profit UE",
        kind="monetary",
        direction="higher_is_better",
        description="Gross profit margin per order.",
        chart_type="line",
    ),
    "Lead Penetration": MetricDefinition(
        name="Lead Penetration",
        kind="ratio",
        direction="higher_is_better",
        description="Enabled stores divided by total lead universe.",
        chart_type="bar",
    ),
    "MLTV Top Verticals Adoption": MetricDefinition(
        name="MLTV Top Verticals Adoption",
        kind="ratio",
        direction="higher_is_better",
        description="User adoption across top verticals.",
    ),
    "Non-Pro PTC > OP": MetricDefinition(
        name="Non-Pro PTC > OP",
        kind="ratio",
        direction="higher_is_better",
        description="Non-Pro conversion from proceed-to-checkout to order placed.",
    ),
    "Perfect Orders": MetricDefinition(
        name="Perfect Orders",
        kind="ratio",
        direction="higher_is_better",
        description="Orders without cancellation, defect, or delay.",
        chart_type="bar",
    ),
    "Pro Adoption (Last Week Status)": MetricDefinition(
        name="Pro Adoption (Last Week Status)",
        kind="ratio",
        direction="higher_is_better",
        description="Share of users with Pro subscription.",
    ),
    "Restaurants Markdowns / GMV": MetricDefinition(
        name="Restaurants Markdowns / GMV",
        kind="ratio",
        direction="lower_is_better",
        description="Discount spend over restaurant GMV.",
    ),
    "Restaurants SS > ATC CVR": MetricDefinition(
        name="Restaurants SS > ATC CVR",
        kind="ratio",
        direction="higher_is_better",
        description="Restaurant conversion from select store to add to cart.",
    ),
    "Restaurants SST > SS CVR": MetricDefinition(
        name="Restaurants SST > SS CVR",
        kind="ratio",
        direction="higher_is_better",
        description="Restaurant conversion from surface/store type to store selection.",
    ),
    "Retail SST > SS CVR": MetricDefinition(
        name="Retail SST > SS CVR",
        kind="ratio",
        direction="higher_is_better",
        description="Retail conversion from surface/store type to store selection.",
    ),
    "Turbo Adoption": MetricDefinition(
        name="Turbo Adoption",
        kind="ratio",
        direction="higher_is_better",
        description="Share of users buying with Turbo available.",
    ),
    "Orders": MetricDefinition(
        name="Orders",
        kind="count",
        direction="higher_is_better",
        description="Order volume in the week.",
        chart_type="line",
    ),
}
