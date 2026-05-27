"""
Reusable CSV business analysis template.

Quick run from the Coffee_Sales folder:
    python business_csv_analyzer.py --input raw_coffee_sales.csv

Default outputs:
    analysis_output/<file_name>_cleaned.csv
    analysis_output/<file_name>_business_report.md
    analysis_output/charts/*.png

This script is designed to be reused across different CSV files:
- Automatically cleans common issues: column names, blank strings, currency,
  percent values, mixed date formats, duplicate rows, and basic missing values.
- Automatically creates KPIs when revenue, cost, and unit columns are available.
- Automatically creates charts and writes a senior-analyst-style insight report.
"""

from __future__ import annotations

import argparse
import re
import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
)


DATE_KEYWORDS = ("date", "day", "month", "year", "time", "created", "updated")
ID_KEYWORDS = ("id", "key", "code", "sku", "uuid")
MEASURE_KEYWORDS = (
    "amount",
    "revenue",
    "sales",
    "cost",
    "expense",
    "profit",
    "margin",
    "price",
    "unit",
    "quantity",
    "qty",
    "discount",
    "tax",
    "total",
    "cogs",
)
DIMENSION_PRIORITY = (
    "region",
    "country",
    "state",
    "city",
    "store",
    "branch",
    "channel",
    "segment",
    "category",
    "subcategory",
    "product",
    "customer",
    "sales_rep",
)
TIME_FEATURES = {"month", "year", "quarter", "day_name", "week_start"}


@dataclass
class ColumnRoles:
    date: str | None = None
    revenue: str | None = None
    cost: str | None = None
    profit: str | None = None
    margin: str | None = None
    units: str | None = None
    discount: str | None = None
    order_id: str | None = None
    dimensions: list[str] | None = None
    numeric: list[str] | None = None

    def __post_init__(self) -> None:
        self.dimensions = self.dimensions or []
        self.numeric = self.numeric or []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean a CSV, create charts, and generate an automated business insight report.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        default="raw_coffee_sales.csv",
        help="Path to the CSV file to analyze.",
    )
    parser.add_argument(
        "--output-dir",
        default="analysis_output",
        help="Folder for the cleaned CSV, charts, and report.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="CSV encoding. If Unicode decoding fails, the script retries with cp1252.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top/bottom groups to show in charts and the report.",
    )
    parser.add_argument(
        "--no-title-case",
        action="store_true",
        help="Do not auto title-case text dimension columns.",
    )
    return parser.parse_args()


def snake_case(name: object) -> str:
    text = str(name).strip()
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", text)
    text = re.sub(r"[^0-9a-zA-Z]+", "_", text)
    text = text.strip("_").lower()
    text = re.sub(r"_+", "_", text)
    return text or "unnamed_column"


def make_unique(names: Iterable[str]) -> list[str]:
    seen: dict[str, int] = {}
    unique_names: list[str] = []
    for name in names:
        count = seen.get(name, 0)
        unique_name = name if count == 0 else f"{name}_{count + 1}"
        seen[name] = count + 1
        unique_names.append(unique_name)
    return unique_names


def is_id_like(column: str) -> bool:
    tokens = set(column.split("_"))
    return any(keyword in tokens or column.endswith(f"_{keyword}") for keyword in ID_KEYWORDS)


def is_date_like_name(column: str) -> bool:
    return any(keyword in column for keyword in DATE_KEYWORDS)


def is_measure_like_name(column: str) -> bool:
    return any(keyword in column for keyword in MEASURE_KEYWORDS)


def clean_string_values(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.str.replace(r"\s+", " ", regex=True)
    blank_tokens = {"", "na", "n/a", "nan", "none", "null", "-", "--"}
    return cleaned.mask(cleaned.str.lower().isin(blank_tokens))


def parse_date_series(series: pd.Series) -> tuple[pd.Series, float]:
    non_null = series.dropna()
    if non_null.empty:
        return pd.to_datetime(series, errors="coerce"), 0.0

    try:
        parsed = pd.to_datetime(series, errors="coerce", format="mixed")
    except TypeError:
        parsed = pd.to_datetime(series, errors="coerce")

    ratio = float(parsed.notna().sum() / max(non_null.shape[0], 1))
    return parsed, ratio


def parse_numeric_series(series: pd.Series) -> tuple[pd.Series, float]:
    non_null = series.dropna()
    if non_null.empty:
        return pd.to_numeric(series, errors="coerce"), 0.0

    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    cleaned = cleaned.str.replace(",", "", regex=False)
    cleaned = cleaned.str.replace("$", "", regex=False)
    cleaned = cleaned.str.replace("%", "", regex=False)
    cleaned = cleaned.str.replace(r"[^0-9.\-]", "", regex=True)
    numeric = pd.to_numeric(cleaned, errors="coerce")
    ratio = float(numeric.notna().sum() / max(non_null.shape[0], 1))
    return numeric, ratio


def smart_title(value: object) -> object:
    if pd.isna(value):
        return value
    text = str(value).strip()
    if not text:
        return pd.NA
    if re.fullmatch(r"[A-Z0-9_-]{2,}", text):
        return text
    if "@" in text or text.startswith(("http://", "https://")):
        return text
    return text.title()


def should_title_case(series: pd.Series, column: str) -> bool:
    if is_id_like(column) or is_measure_like_name(column) or is_date_like_name(column):
        return False
    non_null_count = int(series.notna().sum())
    if non_null_count == 0:
        return False
    unique_ratio = series.nunique(dropna=True) / max(non_null_count, 1)
    return not (non_null_count > 20 and unique_ratio > 0.75)


def find_first_column(
    columns: list[str],
    exact: Iterable[str],
    contains: Iterable[str],
    exclude: Iterable[str] = (),
) -> str | None:
    excluded = tuple(exclude)
    exact_set = set(exact)
    for column in columns:
        if column in exact_set and not any(token in column for token in excluded):
            return column
    for column in columns:
        if any(token in column for token in contains) and not any(token in column for token in excluded):
            return column
    return None


def infer_roles(df: pd.DataFrame) -> ColumnRoles:
    columns = list(df.columns)
    numeric_columns = [column for column in columns if is_numeric_dtype(df[column])]

    roles = ColumnRoles()
    roles.order_id = find_first_column(
        columns,
        exact=("order_id", "transaction_id", "invoice_id", "receipt_id"),
        contains=("order_id", "transaction", "invoice", "receipt"),
    )
    roles.date = find_first_column(
        columns,
        exact=("date", "order_date", "transaction_date", "invoice_date", "created_at"),
        contains=("date", "created_at", "transaction_time"),
    )
    if roles.date is None:
        for column in columns:
            if is_datetime64_any_dtype(df[column]):
                roles.date = column
                break

    roles.revenue = find_first_column(
        numeric_columns,
        exact=(
            "revenue",
            "sales",
            "net_sales",
            "gross_sales",
            "total_sales",
            "amount",
            "total_amount",
        ),
        contains=("revenue", "sales", "amount"),
        exclude=("cost", "unit", "quantity", "qty", "discount"),
    )
    roles.cost = find_first_column(
        numeric_columns,
        exact=("cost", "cogs", "total_cost"),
        contains=("cost", "cogs", "expense"),
        exclude=("revenue", "sales"),
    )
    roles.profit = find_first_column(
        numeric_columns,
        exact=("gross_profit", "profit", "net_profit"),
        contains=("profit",),
        exclude=("margin", "rate"),
    )
    roles.margin = find_first_column(
        numeric_columns,
        exact=("profit_margin", "gross_margin", "margin"),
        contains=("margin",),
    )
    roles.units = find_first_column(
        numeric_columns,
        exact=("units_sold", "quantity", "qty", "units"),
        contains=("units", "quantity", "qty"),
    )
    roles.discount = find_first_column(
        numeric_columns,
        exact=("discount_percent", "discount_rate", "discount"),
        contains=("discount",),
    )
    roles.numeric = numeric_columns
    roles.dimensions = infer_dimensions(df, roles)
    return roles


def infer_dimensions(df: pd.DataFrame, roles: ColumnRoles) -> list[str]:
    excluded = {
        roles.date,
        roles.revenue,
        roles.cost,
        roles.profit,
        roles.margin,
        roles.units,
        roles.discount,
        roles.order_id,
        None,
    }
    dimensions: list[str] = []

    for keyword in DIMENSION_PRIORITY:
        for column in df.columns:
            if column in excluded or column in dimensions or column in TIME_FEATURES:
                continue
            if keyword in column and is_dimension_candidate(df, column):
                dimensions.append(column)

    for column in df.columns:
        if column in excluded or column in dimensions or column in TIME_FEATURES:
            continue
        if is_dimension_candidate(df, column):
            dimensions.append(column)

    return dimensions[:8]


def is_dimension_candidate(df: pd.DataFrame, column: str) -> bool:
    if is_id_like(column) or is_date_like_name(column) or is_measure_like_name(column):
        return False
    if is_object_dtype(df[column]) or is_string_dtype(df[column]):
        return True
    if is_numeric_dtype(df[column]):
        non_null = int(df[column].notna().sum())
        if non_null == 0:
            return False
        unique_count = int(df[column].nunique(dropna=True))
        return unique_count <= min(12, max(3, non_null // 10))
    return False


def load_csv(path: Path, encoding: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path, encoding=encoding)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp1252")


def clean_dataframe(
    raw_df: pd.DataFrame,
    *,
    title_case_text: bool = True,
) -> tuple[pd.DataFrame, dict[str, object]]:
    cleaned = raw_df.copy()
    original_columns = list(cleaned.columns)
    normalized_columns = make_unique(snake_case(column) for column in cleaned.columns)
    cleaned.columns = normalized_columns

    profile: dict[str, object] = {
        "original_shape": raw_df.shape,
        "column_mapping": list(zip(original_columns, normalized_columns)),
        "parsed_date_columns": {},
        "converted_numeric_columns": {},
        "filled_missing_values": {},
        "duplicate_rows_removed": 0,
        "rows_removed": 0,
    }

    for column in cleaned.columns:
        if is_object_dtype(cleaned[column]) or is_string_dtype(cleaned[column]):
            cleaned[column] = clean_string_values(cleaned[column])

    profile["missing_before"] = cleaned.isna().sum().to_dict()

    parsed_date_columns: dict[str, float] = {}
    for column in list(cleaned.columns):
        if not (is_object_dtype(cleaned[column]) or is_string_dtype(cleaned[column])):
            continue
        if is_id_like(column):
            continue
        parsed, ratio = parse_date_series(cleaned[column])
        if (is_date_like_name(column) and ratio >= 0.50) or ratio >= 0.95:
            cleaned[column] = parsed
            parsed_date_columns[column] = round(ratio, 3)

    converted_numeric_columns: dict[str, float] = {}
    for column in list(cleaned.columns):
        if is_datetime64_any_dtype(cleaned[column]) or is_id_like(column):
            continue
        if not (is_object_dtype(cleaned[column]) or is_string_dtype(cleaned[column])):
            continue
        numeric, ratio = parse_numeric_series(cleaned[column])
        should_convert = (is_measure_like_name(column) and ratio >= 0.50) or ratio >= 0.95
        if should_convert:
            cleaned[column] = numeric
            converted_numeric_columns[column] = round(ratio, 3)

    for column in list(cleaned.columns):
        if not (is_object_dtype(cleaned[column]) or is_string_dtype(cleaned[column])):
            continue
        cleaned[column] = clean_string_values(cleaned[column])
        if title_case_text and should_title_case(cleaned[column], column):
            cleaned[column] = cleaned[column].map(smart_title).astype("string")

    duplicate_count = int(cleaned.duplicated().sum())
    if duplicate_count:
        cleaned = cleaned.drop_duplicates().reset_index(drop=True)

    roles_before_fill = infer_roles(cleaned)
    filled_missing: dict[str, str] = {}
    for column in cleaned.columns:
        missing_count = int(cleaned[column].isna().sum())
        if missing_count == 0:
            continue

        if is_datetime64_any_dtype(cleaned[column]):
            filled_missing[column] = "kept as missing date"
            continue

        if is_numeric_dtype(cleaned[column]):
            if column == roles_before_fill.discount or "discount" in column:
                fill_value = 0
                cleaned[column] = cleaned[column].fillna(fill_value)
            else:
                median = cleaned[column].median()
                fill_value = 0 if pd.isna(median) else median
                cleaned[column] = cleaned[column].fillna(fill_value)
            filled_missing[column] = f"filled {missing_count} with {fill_value}"
            continue

        cleaned[column] = cleaned[column].fillna("Unknown")
        filled_missing[column] = f"filled {missing_count} with Unknown"

    for column in cleaned.columns:
        if "percent" in column or column.endswith("_rate"):
            if is_numeric_dtype(cleaned[column]) and cleaned[column].dropna().between(0, 1).all():
                cleaned[column] = cleaned[column] * 100

    profile["parsed_date_columns"] = parsed_date_columns
    profile["converted_numeric_columns"] = converted_numeric_columns
    profile["duplicate_rows_removed"] = duplicate_count
    profile["rows_removed"] = int(raw_df.shape[0] - cleaned.shape[0])
    profile["filled_missing_values"] = filled_missing
    profile["missing_after_cleaning"] = cleaned.isna().sum().to_dict()
    profile["cleaned_shape_before_metrics"] = cleaned.shape
    return cleaned, profile


def enrich_business_metrics(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    roles = infer_roles(enriched)

    if roles.revenue and roles.cost:
        enriched["gross_profit"] = enriched[roles.revenue] - enriched[roles.cost]

    roles = infer_roles(enriched)
    if roles.profit and roles.revenue:
        revenue = enriched[roles.revenue].replace(0, np.nan)
        enriched["profit_margin"] = (enriched[roles.profit] / revenue).replace([np.inf, -np.inf], np.nan)

    roles = infer_roles(enriched)
    if roles.revenue and roles.units:
        units = enriched[roles.units].replace(0, np.nan)
        enriched["avg_price_per_unit"] = (enriched[roles.revenue] / units).replace([np.inf, -np.inf], np.nan)

    roles = infer_roles(enriched)
    if roles.date and is_datetime64_any_dtype(enriched[roles.date]):
        date_values = enriched[roles.date]
        enriched["month"] = date_values.dt.to_period("M").astype("string")
        enriched["year"] = date_values.dt.year.astype("Int64")
        enriched["day_name"] = date_values.dt.day_name()
        enriched["week_start"] = date_values.dt.to_period("W").dt.start_time.dt.date.astype("string")

    return enriched


def format_number(value: object, decimals: int = 0) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    number = float(value)
    return f"{number:,.{decimals}f}"


def format_currency(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"${float(value):,.2f}"


def format_percent_ratio(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:.1f}%"


def format_percent_value(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):.1f}%"


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    if not rows:
        return "_No suitable data available._"

    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join("---" for _ in headers) + " |"
    body_lines = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header_line, separator_line, *body_lines])


def safe_filename(text: str) -> str:
    return re.sub(r"[^0-9a-zA-Z_-]+", "_", text).strip("_").lower()


def wrap_labels(labels: Iterable[object], width: int = 24) -> list[str]:
    return [textwrap.fill(str(label), width=width) for label in labels]


def apply_chart_style() -> None:
    try:
        plt.style.use("seaborn-v0_8-whitegrid")
    except OSError:
        plt.style.use("default")


def save_figure(fig: plt.Figure, path: Path) -> Path:
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def create_charts(
    df: pd.DataFrame,
    roles: ColumnRoles,
    profile: dict[str, object],
    charts_dir: Path,
    top_n: int,
) -> tuple[list[Path], list[str]]:
    charts_dir.mkdir(parents=True, exist_ok=True)
    apply_chart_style()
    chart_paths: list[Path] = []
    chart_errors: list[str] = []

    def attempt(name: str, func) -> None:
        try:
            path = func()
            if path:
                chart_paths.append(path)
        except Exception as exc:  # Chart should not block the report.
            chart_errors.append(f"{name}: {exc}")

    if roles.date and roles.revenue:
        attempt("revenue_trend", lambda: plot_revenue_trend(df, roles, charts_dir))

    for dimension in roles.dimensions[:4]:
        if roles.revenue:
            attempt(
                f"revenue_by_{dimension}",
                lambda dimension=dimension: plot_bar_metric(
                    df=df,
                    dimension=dimension,
                    metric=roles.revenue,
                    charts_dir=charts_dir,
                    top_n=top_n,
                    title=f"Top {top_n} {dimension.replace('_', ' ')} by revenue",
                    filename=f"top_{safe_filename(dimension)}_by_revenue.png",
                    x_label="Revenue",
                ),
            )

        if roles.margin:
            attempt(
                f"margin_by_{dimension}",
                lambda dimension=dimension: plot_margin_by_dimension(df, roles, dimension, charts_dir, top_n),
            )

    if roles.discount and roles.margin:
        attempt("discount_vs_margin", lambda: plot_discount_vs_margin(df, roles, charts_dir))

    attempt("numeric_correlation", lambda: plot_correlation_heatmap(df, charts_dir))
    attempt("missing_values", lambda: plot_missing_values(profile, charts_dir))

    return chart_paths, chart_errors


def plot_revenue_trend(df: pd.DataFrame, roles: ColumnRoles, charts_dir: Path) -> Path | None:
    trend_data = df.dropna(subset=[roles.date, roles.revenue]).copy()
    if trend_data.empty:
        return None

    date_span = trend_data[roles.date].max() - trend_data[roles.date].min()
    frequency = "MS" if date_span.days > 120 else "D"
    grouped = (
        trend_data.set_index(roles.date)
        .resample(frequency)[[column for column in [roles.revenue, roles.profit] if column]]
        .sum()
        .dropna(how="all")
    )
    if grouped.empty:
        return None

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(grouped.index, grouped[roles.revenue], marker="o", linewidth=2, label="Revenue")
    if roles.profit and roles.profit in grouped:
        ax.plot(grouped.index, grouped[roles.profit], marker="o", linewidth=2, label="Gross profit")
    ax.set_title("Revenue and profit trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()
    ax.tick_params(axis="x", rotation=35)
    return save_figure(fig, charts_dir / "revenue_profit_trend.png")


def plot_bar_metric(
    *,
    df: pd.DataFrame,
    dimension: str,
    metric: str,
    charts_dir: Path,
    top_n: int,
    title: str,
    filename: str,
    x_label: str,
) -> Path | None:
    grouped = (
        df.dropna(subset=[dimension])
        .groupby(dimension, dropna=False)[metric]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .sort_values()
    )
    if grouped.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, max(4.5, len(grouped) * 0.55)))
    y_positions = np.arange(len(grouped))
    ax.barh(y_positions, grouped.values, color="#2f6f73")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(wrap_labels(grouped.index))
    ax.set_title(title)
    ax.set_xlabel(x_label)
    for index, value in enumerate(grouped.values):
        ax.text(value, index, f" {value:,.0f}", va="center", fontsize=9)
    return save_figure(fig, charts_dir / filename)


def plot_margin_by_dimension(
    df: pd.DataFrame,
    roles: ColumnRoles,
    dimension: str,
    charts_dir: Path,
    top_n: int,
) -> Path | None:
    if not roles.revenue or not roles.profit:
        return None

    grouped = (
        df.dropna(subset=[dimension])
        .groupby(dimension, dropna=False)
        .agg(revenue=(roles.revenue, "sum"), profit=(roles.profit, "sum"))
    )
    grouped = grouped[grouped["revenue"] > 0]
    if grouped.empty:
        return None

    grouped["margin"] = grouped["profit"] / grouped["revenue"]
    grouped = grouped.sort_values("revenue", ascending=False).head(top_n).sort_values("margin")
    fig, ax = plt.subplots(figsize=(10, max(4.5, len(grouped) * 0.55)))
    y_positions = np.arange(len(grouped))
    ax.barh(y_positions, grouped["margin"] * 100, color="#7c5c2e")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(wrap_labels(grouped.index))
    ax.set_title(f"Profit margin by {dimension.replace('_', ' ')}")
    ax.set_xlabel("Profit margin (%)")
    for index, value in enumerate(grouped["margin"] * 100):
        ax.text(value, index, f" {value:.1f}%", va="center", fontsize=9)
    return save_figure(fig, charts_dir / f"margin_by_{safe_filename(dimension)}.png")


def plot_discount_vs_margin(df: pd.DataFrame, roles: ColumnRoles, charts_dir: Path) -> Path | None:
    data = df[[roles.discount, roles.margin]].dropna().copy()
    if data.empty:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(data[roles.discount], data[roles.margin] * 100, alpha=0.7, color="#4d72b0")
    ax.set_title("Discount vs profit margin")
    ax.set_xlabel("Discount (%)")
    ax.set_ylabel("Profit margin (%)")
    return save_figure(fig, charts_dir / "discount_vs_profit_margin.png")


def plot_correlation_heatmap(df: pd.DataFrame, charts_dir: Path) -> Path | None:
    numeric_columns = [
        column
        for column in df.columns
        if is_numeric_dtype(df[column]) and not is_id_like(column) and df[column].nunique(dropna=True) > 1
    ][:10]
    if len(numeric_columns) < 2:
        return None

    corr = df[numeric_columns].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(max(7, len(numeric_columns) * 0.9), max(6, len(numeric_columns) * 0.75)))
    image = ax.imshow(corr, cmap="RdYlGn", vmin=-1, vmax=1)
    ax.set_xticks(np.arange(len(numeric_columns)))
    ax.set_yticks(np.arange(len(numeric_columns)))
    ax.set_xticklabels(wrap_labels(numeric_columns, width=14), rotation=45, ha="right")
    ax.set_yticklabels(wrap_labels(numeric_columns, width=14))
    ax.set_title("Numeric correlation heatmap")
    for row in range(len(numeric_columns)):
        for col in range(len(numeric_columns)):
            ax.text(col, row, f"{corr.iloc[row, col]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=ax, shrink=0.85)
    return save_figure(fig, charts_dir / "numeric_correlation_heatmap.png")


def plot_missing_values(profile: dict[str, object], charts_dir: Path) -> Path | None:
    missing_before = profile.get("missing_before", {})
    if not isinstance(missing_before, dict):
        return None
    missing_series = pd.Series(missing_before).sort_values(ascending=False)
    missing_series = missing_series[missing_series > 0].head(12)
    if missing_series.empty:
        return None

    fig, ax = plt.subplots(figsize=(9, max(4, len(missing_series) * 0.45)))
    grouped = missing_series.sort_values()
    y_positions = np.arange(len(grouped))
    ax.barh(y_positions, grouped.values, color="#b45f4d")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(wrap_labels(grouped.index))
    ax.set_title("Missing values before cleaning")
    ax.set_xlabel("Missing rows")
    for index, value in enumerate(grouped.values):
        ax.text(value, index, f" {int(value):,}", va="center", fontsize=9)
    return save_figure(fig, charts_dir / "missing_values_before_cleaning.png")


def build_dimension_summary(
    df: pd.DataFrame,
    roles: ColumnRoles,
    dimension: str,
    top_n: int,
) -> pd.DataFrame:
    aggregations: dict[str, tuple[str, str]] = {}
    if roles.revenue:
        aggregations["revenue"] = (roles.revenue, "sum")
    if roles.profit:
        aggregations["profit"] = (roles.profit, "sum")
    if roles.units:
        aggregations["units"] = (roles.units, "sum")
    if not aggregations:
        return pd.DataFrame()

    grouped = df.groupby(dimension, dropna=False).agg(**aggregations)
    if roles.revenue and roles.profit:
        grouped["profit_margin"] = grouped["profit"] / grouped["revenue"].replace(0, np.nan)
    sort_column = "revenue" if "revenue" in grouped else list(grouped.columns)[0]
    return grouped.sort_values(sort_column, ascending=False).head(top_n)


def build_kpi_rows(df: pd.DataFrame, roles: ColumnRoles) -> list[list[str]]:
    rows: list[list[str]] = [["Rows after cleaning", format_number(len(df)), "Dataset size used for analysis"]]
    if roles.date:
        min_date = df[roles.date].min()
        max_date = df[roles.date].max()
        if pd.notna(min_date) and pd.notna(max_date):
            rows.append(["Period", f"{min_date:%Y-%m-%d} -> {max_date:%Y-%m-%d}", "Available data period"])
    if roles.revenue:
        rows.append(["Total revenue", format_currency(df[roles.revenue].sum()), "Total sales/revenue"])
    if roles.profit:
        rows.append(["Gross profit", format_currency(df[roles.profit].sum()), "Gross profit after cost"])
    if roles.revenue and roles.profit and df[roles.revenue].sum() != 0:
        margin = df[roles.profit].sum() / df[roles.revenue].sum()
        rows.append(["Blended margin", format_percent_ratio(margin), "Overall gross profit margin"])
    if roles.units:
        rows.append(["Units sold", format_number(df[roles.units].sum()), "Total volume sold"])
    if roles.order_id:
        rows.append(["Transactions", format_number(df[roles.order_id].nunique()), "Unique orders/transactions"])
    if roles.discount:
        rows.append(["Avg discount", format_percent_value(df[roles.discount].mean()), "Average discount rate"])
    return rows


def build_insights(df: pd.DataFrame, roles: ColumnRoles, top_n: int) -> list[str]:
    insights: list[str] = []

    if roles.revenue:
        total_revenue = float(df[roles.revenue].sum())
        insights.append(f"Total revenue is {format_currency(total_revenue)} across {format_number(len(df))} cleaned rows.")

    if roles.revenue and roles.profit and df[roles.revenue].sum() != 0:
        margin = df[roles.profit].sum() / df[roles.revenue].sum()
        insights.append(
            f"Overall gross margin is {format_percent_ratio(margin)}; this KPI should be tracked alongside revenue growth."
        )

    if roles.date and roles.revenue:
        trend = calculate_period_trend(df, roles)
        if trend:
            insights.append(trend)

    for dimension in roles.dimensions[:3]:
        summary = build_dimension_summary(df, roles, dimension, top_n)
        if summary.empty:
            continue
        top_name = summary.index[0]
        if roles.revenue and "revenue" in summary:
            share = summary.iloc[0]["revenue"] / max(df[roles.revenue].sum(), 1)
            insights.append(
                f"The strongest {dimension.replace('_', ' ')} is '{top_name}' with "
                f"{format_currency(summary.iloc[0]['revenue'])}, contributing {format_percent_ratio(share)} of revenue."
            )
        if "profit_margin" in summary and summary["profit_margin"].notna().any():
            low_margin = summary.sort_values("profit_margin").iloc[0]
            insights.append(
                f"Within {dimension.replace('_', ' ')} groups, '{low_margin.name}' has the lowest margin "
                f"({format_percent_ratio(low_margin['profit_margin'])}) among top revenue groups; review pricing, COGS, or promotion strategy."
            )

    if roles.discount and roles.margin:
        discount_insight = calculate_discount_insight(df, roles)
        if discount_insight:
            insights.append(discount_insight)

    return insights[:10]


def calculate_period_trend(df: pd.DataFrame, roles: ColumnRoles) -> str | None:
    data = df.dropna(subset=[roles.date, roles.revenue]).copy()
    if data.empty:
        return None
    date_span = data[roles.date].max() - data[roles.date].min()
    frequency = "MS" if date_span.days > 120 else "D"
    period_revenue = data.set_index(roles.date).resample(frequency)[roles.revenue].sum()
    period_revenue = period_revenue[period_revenue > 0]
    if len(period_revenue) < 2:
        return None
    first_value = float(period_revenue.iloc[0])
    last_value = float(period_revenue.iloc[-1])
    if first_value == 0:
        return None
    change = (last_value - first_value) / abs(first_value)
    direction = "increased" if change >= 0 else "decreased"
    return (
        f"Revenue in the final period {direction} by {abs(change) * 100:.1f}% versus the first period "
        f"({format_currency(first_value)} -> {format_currency(last_value)})."
    )


def calculate_discount_insight(df: pd.DataFrame, roles: ColumnRoles) -> str | None:
    data = df[[roles.discount, roles.margin]].dropna().copy()
    if data.empty:
        return None

    discounted = data[data[roles.discount] > 0]
    full_price = data[data[roles.discount] == 0]
    if discounted.empty or full_price.empty:
        return None

    discounted_margin = discounted[roles.margin].mean()
    full_price_margin = full_price[roles.margin].mean()
    difference = discounted_margin - full_price_margin
    direction = "higher than" if difference >= 0 else "lower than"
    return (
        f"Discounted rows have an average margin of {format_percent_ratio(discounted_margin)}, "
        f"{abs(difference) * 100:.1f} percentage points {direction} non-discounted rows. "
        "This is a signal to evaluate whether promotions are creating value or eroding profit."
    )


def build_recommendations(df: pd.DataFrame, roles: ColumnRoles) -> list[str]:
    recommendations: list[str] = []

    if roles.dimensions and roles.revenue:
        primary_dimension = roles.dimensions[0]
        summary = build_dimension_summary(df, roles, primary_dimension, top_n=10)
        if not summary.empty and "revenue" in summary:
            top_name = summary.index[0]
            recommendations.append(
                f"Double down on '{top_name}' in the {primary_dimension.replace('_', ' ')} dimension: "
                "review inventory, staffing, campaigns, and cross-sell opportunities to expand the revenue-driving group."
            )

    if roles.revenue and roles.profit and roles.dimensions:
        for dimension in roles.dimensions[:3]:
            summary = build_dimension_summary(df, roles, dimension, top_n=20)
            if "profit_margin" not in summary or summary.empty:
                continue
            revenue_median = summary["revenue"].median()
            candidates = summary[(summary["revenue"] >= revenue_median) & summary["profit_margin"].notna()]
            if candidates.empty:
                continue
            low_margin = candidates.sort_values("profit_margin").iloc[0]
            recommendations.append(
                f"Investigate the margin for '{low_margin.name}' ({dimension.replace('_', ' ')}): "
                f"revenue is meaningful, but margin is only {format_percent_ratio(low_margin['profit_margin'])}. "
                "Prioritize reviewing cost, price packs, discounting, and product mix."
            )
            break

    if roles.discount and roles.margin:
        recommendations.append(
            "Split promotions into clear cohorts: no discount, light discount, and deep discount. "
            "Compare incremental revenue with margin loss before increasing promotional spend."
        )

    if roles.date and roles.revenue:
        recommendations.append(
            "Build a daily/weekly dashboard for revenue, gross profit, and margin to detect slow sales days, "
            "stockout risk, or underperforming campaigns early."
        )

    if not recommendations:
        recommendations.append(
            "Add a data dictionary and map revenue/cost/date/category columns so the automated report can generate deeper insights."
        )

    return recommendations[:6]


def build_data_quality_rows(profile: dict[str, object]) -> list[list[str]]:
    original_shape = profile.get("original_shape", (0, 0))
    cleaned_shape = profile.get("cleaned_shape_after_metrics", profile.get("cleaned_shape_before_metrics", (0, 0)))
    rows = [
        ["Original shape", f"{original_shape[0]:,} rows x {original_shape[1]:,} columns"],
        ["Shape after cleaning/metrics", f"{cleaned_shape[0]:,} rows x {cleaned_shape[1]:,} columns"],
        ["Duplicate rows removed", format_number(profile.get("duplicate_rows_removed", 0))],
    ]

    parsed_dates = profile.get("parsed_date_columns", {})
    if isinstance(parsed_dates, dict) and parsed_dates:
        rows.append(["Date columns parsed", ", ".join(f"{column} ({ratio:.0%})" for column, ratio in parsed_dates.items())])

    converted_numeric = profile.get("converted_numeric_columns", {})
    if isinstance(converted_numeric, dict) and converted_numeric:
        rows.append(["Numeric columns converted", ", ".join(f"{column} ({ratio:.0%})" for column, ratio in converted_numeric.items())])

    filled_missing = profile.get("filled_missing_values", {})
    if isinstance(filled_missing, dict) and filled_missing:
        rows.append(["Missing values handled", "; ".join(f"{column}: {rule}" for column, rule in filled_missing.items())])

    return rows


def build_report(
    *,
    input_path: Path,
    cleaned_path: Path,
    df: pd.DataFrame,
    roles: ColumnRoles,
    profile: dict[str, object],
    chart_paths: list[Path],
    chart_errors: list[str],
    top_n: int,
) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines: list[str] = [
        f"# Business Insight Report - {input_path.name}",
        "",
        f"Generated at: {generated_at}",
        "",
        "## Executive Summary",
        "",
    ]

    insights = build_insights(df, roles, top_n)
    if insights:
        report_lines.extend(f"- {insight}" for insight in insights)
    else:
        report_lines.append(
            "- The dataset was cleaned and profiled, but it does not yet contain enough core business columns for deeper insights."
        )

    report_lines.extend(
        [
            "",
            "## KPI Snapshot",
            "",
            markdown_table(["KPI", "Value", "Why it matters"], build_kpi_rows(df, roles)),
            "",
            "## Data Quality Summary",
            "",
            markdown_table(["Check", "Result"], build_data_quality_rows(profile)),
            "",
            "## Dimension Performance",
            "",
        ]
    )

    if roles.dimensions:
        for dimension in roles.dimensions[:3]:
            summary = build_dimension_summary(df, roles, dimension, top_n)
            if summary.empty:
                continue
            report_lines.extend([f"### Top {dimension.replace('_', ' ').title()}", ""])
            rows: list[list[str]] = []
            for name, row in summary.iterrows():
                table_row = [str(name)]
                if "revenue" in summary:
                    table_row.append(format_currency(row["revenue"]))
                if "profit" in summary:
                    table_row.append(format_currency(row["profit"]))
                if "profit_margin" in summary:
                    table_row.append(format_percent_ratio(row["profit_margin"]))
                if "units" in summary:
                    table_row.append(format_number(row["units"]))
                rows.append(table_row)

            headers = [dimension.replace("_", " ").title()]
            if "revenue" in summary:
                headers.append("Revenue")
            if "profit" in summary:
                headers.append("Profit")
            if "profit_margin" in summary:
                headers.append("Margin")
            if "units" in summary:
                headers.append("Units")
            report_lines.extend([markdown_table(headers, rows), ""])
    else:
        report_lines.extend(["_No clear dimension columns were found for performance grouping._", ""])

    report_lines.extend(
        [
            "## Recommendations",
            "",
            *[f"- {recommendation}" for recommendation in build_recommendations(df, roles)],
            "",
            "## Output Files",
            "",
            f"- Cleaned CSV: `{cleaned_path.as_posix()}`",
        ]
    )

    if chart_paths:
        report_lines.append("- Charts:")
        report_lines.extend(f"  - `{path.as_posix()}`" for path in chart_paths)
    else:
        report_lines.append("- Charts: no chart type matched the current schema.")

    if chart_errors:
        report_lines.extend(["", "## Chart Warnings", ""])
        report_lines.extend(f"- {error}" for error in chart_errors)

    report_lines.extend(
        [
            "",
            "## Suggested Next Analyst Steps",
            "",
            "- Validate business definitions: revenue gross/net, cost/COGS, discount before/after tax.",
            "- Add a data dictionary for each column to reduce the risk of incorrect auto-inference.",
            "- Add targets/forecasts to turn this report into variance analysis.",
            "- Connect the cleaned CSV output to a BI dashboard if this pipeline runs daily.",
            "",
        ]
    )

    return "\n".join(report_lines)


def save_outputs(
    *,
    input_path: Path,
    output_dir: Path,
    cleaned_df: pd.DataFrame,
    report: str,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = safe_filename(input_path.stem)
    cleaned_path = output_dir / f"{stem}_cleaned.csv"
    report_path = output_dir / f"{stem}_business_report.md"
    cleaned_df.to_csv(cleaned_path, index=False)
    report_path.write_text(report, encoding="utf-8")
    return cleaned_path, report_path


def resolve_input_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.exists():
        return path

    script_relative_path = Path(__file__).resolve().parent / raw_path
    if script_relative_path.exists():
        return script_relative_path

    raise FileNotFoundError(f"Input file not found: {raw_path}")


def main() -> None:
    args = parse_args()
    input_path = resolve_input_path(args.input)
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = Path.cwd() / output_dir

    raw_df = load_csv(input_path, args.encoding)
    cleaned_df, profile = clean_dataframe(raw_df, title_case_text=not args.no_title_case)
    cleaned_df = enrich_business_metrics(cleaned_df)
    roles = infer_roles(cleaned_df)
    profile["cleaned_shape_after_metrics"] = cleaned_df.shape

    charts_dir = output_dir / "charts"
    chart_paths, chart_errors = create_charts(cleaned_df, roles, profile, charts_dir, args.top_n)

    stem = safe_filename(input_path.stem)
    cleaned_path = output_dir / f"{stem}_cleaned.csv"
    report = build_report(
        input_path=input_path,
        cleaned_path=cleaned_path,
        df=cleaned_df,
        roles=roles,
        profile=profile,
        chart_paths=chart_paths,
        chart_errors=chart_errors,
        top_n=args.top_n,
    )
    cleaned_path, report_path = save_outputs(
        input_path=input_path,
        output_dir=output_dir,
        cleaned_df=cleaned_df,
        report=report,
    )

    print("Done.")
    print(f"Cleaned CSV: {cleaned_path}")
    print(f"Report: {report_path}")
    print(f"Charts: {charts_dir}")
    if chart_errors:
        print("Chart warnings:")
        for error in chart_errors:
            print(f"- {error}")


if __name__ == "__main__":
    main()
