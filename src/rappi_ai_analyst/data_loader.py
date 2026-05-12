from __future__ import annotations

from pathlib import Path

import pandas as pd

from rappi_ai_analyst.models import DatasetBundle

REQUIRED_SHEETS = {"RAW_INPUT_METRICS", "RAW_ORDERS"}
METRIC_WEEK_COLUMNS = [f"L{week}W_ROLL" for week in range(8, -1, -1)]
ORDER_WEEK_COLUMNS = [f"L{week}W" for week in range(8, -1, -1)]
ZONE_KEYS = ["COUNTRY", "CITY", "ZONE"]
ZONE_DIM_COLUMNS = ZONE_KEYS + ["ZONE_TYPE", "ZONE_PRIORITIZATION"]


class DataValidationError(RuntimeError):
    pass


def load_dataset(data_file: Path) -> DatasetBundle:
    if not data_file.exists():
        raise DataValidationError(f"Dataset file not found: {data_file}")

    workbook = pd.ExcelFile(data_file)
    missing_sheets = REQUIRED_SHEETS.difference(workbook.sheet_names)
    if missing_sheets:
        raise DataValidationError(f"Missing required sheets: {sorted(missing_sheets)}")

    metrics_wide = workbook.parse("RAW_INPUT_METRICS")
    orders_wide = workbook.parse("RAW_ORDERS")

    _validate_columns(metrics_wide, ZONE_DIM_COLUMNS + ["METRIC"] + METRIC_WEEK_COLUMNS, "RAW_INPUT_METRICS")
    _validate_columns(orders_wide, ZONE_KEYS + ["METRIC"] + ORDER_WEEK_COLUMNS, "RAW_ORDERS")

    metrics_wide = _deduplicate_rows(metrics_wide)
    orders_wide = _deduplicate_rows(orders_wide)
    metrics_wide = _collapse_semantic_duplicates(metrics_wide)

    metrics_long = _melt_metrics(metrics_wide)
    orders_long = _melt_orders(orders_wide)
    zone_dimension = _build_zone_dimension(metrics_wide)
    join_coverage = _build_join_coverage(metrics_wide, orders_wide)

    return DatasetBundle(
        metrics_wide=metrics_wide,
        metrics_long=metrics_long,
        orders_wide=orders_wide,
        orders_long=orders_long,
        zone_dimension=zone_dimension,
        join_coverage=join_coverage,
    )


def _validate_columns(df: pd.DataFrame, required_columns: list[str], sheet_name: str) -> None:
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise DataValidationError(f"Missing columns in {sheet_name}: {missing}")


def _deduplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


def _collapse_semantic_duplicates(metrics_wide: pd.DataFrame) -> pd.DataFrame:
    return metrics_wide.groupby(
        ZONE_DIM_COLUMNS + ["METRIC"], as_index=False, dropna=False
    )[METRIC_WEEK_COLUMNS].first()


def _melt_metrics(metrics_wide: pd.DataFrame) -> pd.DataFrame:
    melted = metrics_wide.melt(
        id_vars=ZONE_DIM_COLUMNS + ["METRIC"],
        value_vars=METRIC_WEEK_COLUMNS,
        var_name="week_label",
        value_name="value",
    )
    melted["week_index"] = melted["week_label"].str.extract(r"L(\d+)W").astype(int)
    melted["week_recency_rank"] = 8 - melted["week_index"]
    return melted.sort_values(ZONE_DIM_COLUMNS + ["METRIC", "week_index"]).reset_index(drop=True)


def _melt_orders(orders_wide: pd.DataFrame) -> pd.DataFrame:
    melted = orders_wide.melt(
        id_vars=ZONE_KEYS + ["METRIC"],
        value_vars=ORDER_WEEK_COLUMNS,
        var_name="week_label",
        value_name="value",
    )
    melted["week_index"] = melted["week_label"].str.extract(r"L(\d+)W").astype(int)
    melted["week_recency_rank"] = 8 - melted["week_index"]
    return melted.sort_values(ZONE_KEYS + ["METRIC", "week_index"]).reset_index(drop=True)


def _build_zone_dimension(metrics_wide: pd.DataFrame) -> pd.DataFrame:
    zone_dim = metrics_wide[ZONE_DIM_COLUMNS].drop_duplicates().sort_values(ZONE_KEYS).reset_index(drop=True)
    return zone_dim


def _build_join_coverage(metrics_wide: pd.DataFrame, orders_wide: pd.DataFrame) -> pd.DataFrame:
    metric_keys = metrics_wide[ZONE_KEYS].drop_duplicates().assign(in_metrics=True)
    order_keys = orders_wide[ZONE_KEYS].drop_duplicates().assign(in_orders=True)
    coverage = metric_keys.merge(order_keys, on=ZONE_KEYS, how="outer")
    coverage["in_metrics"] = coverage["in_metrics"].eq(True)
    coverage["in_orders"] = coverage["in_orders"].eq(True)
    coverage["coverage_status"] = coverage.apply(
        lambda row: "both"
        if row["in_metrics"] and row["in_orders"]
        else "metrics_only"
        if row["in_metrics"]
        else "orders_only",
        axis=1,
    )
    return coverage.sort_values(ZONE_KEYS).reset_index(drop=True)
