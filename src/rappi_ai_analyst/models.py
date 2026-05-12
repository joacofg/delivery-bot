from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

MetricDirection = Literal["higher_is_better", "lower_is_better", "neutral"]
MetricKind = Literal["ratio", "monetary", "count"]
ChartType = Literal["line", "bar", "table"]


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    kind: MetricKind
    direction: MetricDirection
    description: str
    chart_type: ChartType = "table"


@dataclass(frozen=True)
class DatasetBundle:
    metrics_wide: pd.DataFrame
    metrics_long: pd.DataFrame
    orders_wide: pd.DataFrame
    orders_long: pd.DataFrame
    zone_dimension: pd.DataFrame
    join_coverage: pd.DataFrame
