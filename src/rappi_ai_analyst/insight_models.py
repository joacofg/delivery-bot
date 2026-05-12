from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

InsightCategory = Literal[
    "anomaly",
    "deteriorating_trend",
    "benchmark_gap",
    "correlation",
    "opportunity",
]


@dataclass(frozen=True)
class InsightRecord:
    category: InsightCategory
    title: str
    summary: str
    recommendation: str
    evidence: dict


@dataclass(frozen=True)
class InsightBundle:
    executive_summary: list[InsightRecord]
    anomalies: pd.DataFrame
    deteriorations: pd.DataFrame
    benchmark_gaps: pd.DataFrame
    correlations: pd.DataFrame
    opportunities: pd.DataFrame
