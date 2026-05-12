from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


@dataclass
class RenderPayload:
    title: str
    dataframe: pd.DataFrame
    chart: go.Figure | None
    chart_type: str
    narrative: str
    heuristic_disclosure: str | None
    metadata: dict[str, Any] | None = None


def build_chart(dataframe: pd.DataFrame, chart_type: str, title: str) -> go.Figure | None:
    if dataframe.empty:
        return None

    if chart_type == "line" and {"week_index", "value"}.issubset(dataframe.columns):
        plot_df = dataframe.sort_values("week_index").copy()
        plot_df["week_label_display"] = plot_df["week_label"].str.replace("_ROLL", "", regex=False)
        return px.line(plot_df, x="week_label_display", y="value", markers=True, title=title)

    if chart_type == "bar":
        if {"ZONE", "value"}.issubset(dataframe.columns):
            return px.bar(dataframe, x="ZONE", y="value", color="COUNTRY" if "COUNTRY" in dataframe.columns else None, title=title)
        if {"COUNTRY", "average_value"}.issubset(dataframe.columns):
            return px.bar(dataframe, x="COUNTRY", y="average_value", title=title)
        if {"ZONE_TYPE", "avg_value"}.issubset(dataframe.columns):
            return px.bar(dataframe, x="ZONE_TYPE", y="avg_value", title=title)

    return None


def build_render_payload(title: str, dataframe: pd.DataFrame, chart_type: str, narrative: str, heuristic_disclosure: str | None, metadata: dict[str, Any] | None = None) -> RenderPayload:
    return RenderPayload(
        title=title,
        dataframe=dataframe,
        chart=build_chart(dataframe, chart_type=chart_type, title=title),
        chart_type=chart_type,
        narrative=narrative,
        heuristic_disclosure=heuristic_disclosure,
        metadata=metadata,
    )
