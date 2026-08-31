import re
from datetime import datetime
from typing import Any

import pandas as pd


# -----------------------------
# Generic cleaning helpers
# -----------------------------

def clean_text(value: Any) -> str | None:
    """Normalize text while preserving missing values."""
    if value is None:
        return None

    value = str(value).strip()

    if not value or value.lower() in {
        "nan",
        "none",
        "null",
        "n/a",
        "na",
        "-"
    }:
        return None

    # Normalize repeated whitespace
    value = re.sub(r"\s+", " ", value)

    return value


def clean_number(value: Any) -> float | None:
    """Convert messy numeric values into numbers."""
    if value is None:
        return None

    if isinstance(value, (int, float)):
        if pd.isna(value):
            return None
        return float(value)

    value = str(value).strip()

    if not value or value.lower() in {"nan", "none", "null", "n/a", "na", "-"}:
        return None

    # Remove currency symbols, commas and spaces
    value = re.sub(r"[₹,$,\s]", "", value)

    # Keep digits, decimal point and negative sign
    value = re.sub(r"[^0-9.\-]", "", value)

    try:
        return float(value)
    except ValueError:
        return None


def clean_date(value: Any) -> str | None:
    """Normalize different date representations to YYYY-MM-DD."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")

    value = str(value).strip()

    if not value or value.lower() in {"nan", "none", "null", "n/a", "na", "-"}:
        return None

    parsed = pd.to_datetime(value, errors="coerce", dayfirst=False)

    if pd.isna(parsed):
        return None

    return parsed.strftime("%Y-%m-%d")


# -----------------------------
# Domain normalization
# -----------------------------

def normalize_sector(value: Any) -> str | None:
    value = clean_text(value)

    if not value:
        return None

    normalized = value.lower().strip()

    sector_map = {
        "energy": "Energy",
        "energy sector": "Energy",

        "renewable": "Renewables",
        "renewables": "Renewables",
        "renewable energy": "Renewables",

        "oil & gas": "Oil & Gas",
        "oil and gas": "Oil & Gas",
        "oilandgas": "Oil & Gas",

        "powerline": "Powerline",

        "infrastructure": "Infrastructure",
        "infra": "Infrastructure",

        "construction": "Construction",
        "mining": "Mining",
        "agriculture": "Agriculture",
        "aviation": "Aviation",
        "railways": "Railways",
        "manufacturing": "Manufacturing",

        "security and surveillance": "Security And Surveillance",

        "dsp": "Dsp",
        "tender": "Tender",
        "others": "Others",
        "sector/service": "Sector/Service",
    }

    return sector_map.get(
        normalized,
        value.title()
    )
def normalize_status(value: Any) -> str | None:
    value = clean_text(value)

    if not value:
        return None

    normalized = value.lower().strip()

    status_map = {
        "won": "Won",
        "closed won": "Won",
        "lost": "Lost",
        "closed lost": "Lost",
        "open": "Open",
        "active": "Active",
        "in progress": "In Progress",
        "in-progress": "In Progress",
        "completed": "Completed",
        "complete": "Completed",
        "pending": "Pending",
        "cancelled": "Cancelled",
        "canceled": "Cancelled",
    }

    return status_map.get(
        normalized,
        value.title()
    )

# -----------------------------
# Monday item conversion
# -----------------------------

def monday_items_to_dataframe(board_response: dict) -> pd.DataFrame:
    """
    Convert monday.com GraphQL response into a DataFrame
    using the board's actual column titles.
    """

    boards = board_response.get("boards", [])

    if not boards:
        return pd.DataFrame()

    board = boards[0]

    # Build:
    # Monday column ID -> human-readable column title
    column_map = {
        column["id"]: column["title"]
        for column in board.get("columns", [])
    }

    items = board.get("items_page", {}).get("items", [])

    rows = []

    for item in items:

        row = {
            "item_id": item.get("id"),
            "item_name": clean_text(item.get("name")),
        }

        for column in item.get("column_values", []):

            column_id = column.get("id")

            column_name = column_map.get(
                column_id,
                column_id
            )

            row[column_name] = clean_text(
                column.get("text")
            )

        rows.append(row)

    return pd.DataFrame(rows)


# -----------------------------
# Deals processing
# -----------------------------

def process_deals(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Clean and normalize Deals data.

    Returns:
        cleaned dataframe
        data quality warnings
    """

    warnings = []

    if df.empty:
        return df, ["Deals board returned no records."]

    result = df.copy()

    # Normalize every text-like column first
    for column in result.columns:
        result[column] = result[column].apply(clean_text)

    # Detect likely fields by column name
    for column in result.columns:
        name = column.lower()

        if "date" in name:
            result[column] = result[column].apply(clean_date)

        if "value" in name or "amount" in name:
            result[column] = result[column].apply(clean_number)

        if "sector" in name:
            result[column] = result[column].apply(normalize_sector)

        if "status" in name or "stage" in name:
            result[column] = result[column].apply(normalize_status)

    # Quality checks
    missing_counts = result.isna().sum()

    important_fields = [
        column for column in result.columns
        if any(keyword in column.lower()
               for keyword in ["sector", "status", "value", "date"])
    ]

    for column in important_fields:
        missing = int(missing_counts.get(column, 0))

        if missing:
            warnings.append(
                f"{column}: {missing} record(s) have missing values."
            )

    return result, warnings


# -----------------------------
# Work Orders processing
# -----------------------------

def process_work_orders(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Clean and normalize Work Orders data.
    """

    warnings = []

    if df.empty:
        return df, ["Work Orders board returned no records."]

    result = df.copy()
    if "item_name" in result.columns:
        result = result[
            result["item_name"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            != "deal name masked"
        ].copy()

    # Normalize text
    for column in result.columns:
        result[column] = result[column].apply(clean_text)

    # Normalize fields based on their names
    for column in result.columns:
        name = column.lower()

        if "date" in name or "month" in name:
            result[column] = result[column].apply(clean_date)

        if (
            "amount" in name
            or "value" in name
            or "quantity" in name
            or "hours" in name
        ):
            result[column] = result[column].apply(clean_number)

        if "sector" in name:
            result[column] = result[column].apply(normalize_sector)

        if "status" in name:
            result[column] = result[column].apply(normalize_status)

    # Quality checks
    missing_counts = result.isna().sum()

    important_fields = [
        column for column in result.columns
        if any(keyword in column.lower()
               for keyword in [
                   "sector",
                   "status",
                   "amount",
                   "date",
                   "quantity"
               ])
    ]

    for column in important_fields:
        missing = int(missing_counts.get(column, 0))

        if missing:
            warnings.append(
                f"{column}: {missing} record(s) have missing values."
            )

    return result, warnings