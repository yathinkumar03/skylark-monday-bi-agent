import pandas as pd
from datetime import datetime


# =============================================================
# HELPER FUNCTIONS
# =============================================================

def find_column(df, keywords):
    """
    Find a column containing all supplied keywords.
    """

    for column in df.columns:

        column_name = str(column).lower()

        if all(
            keyword.lower() in column_name
            for keyword in keywords
        ):
            return column

    return None


def to_numeric(series):
    """
    Safely convert a pandas Series to numeric.
    """

    return pd.to_numeric(
        series,
        errors="coerce"
    )


def parse_dates(series):
    """
    Safely convert a pandas Series to datetime.
    """

    return pd.to_datetime(
        series,
        errors="coerce"
    )


def quarter_start(date):
    """
    Return the first day of the quarter containing date.
    """

    month = ((date.month - 1) // 3) * 3 + 1

    return pd.Timestamp(
        year=date.year,
        month=month,
        day=1
    )


def quarter_end(date):
    """
    Return the last day of the quarter containing date.
    """

    start = quarter_start(date)

    return (
        start
        + pd.offsets.QuarterEnd()
    )


def get_latest_data_date(df):
    """
    Determine the latest meaningful date available
    in the Deals data.

    Priority:
    1. Tentative Close Date
    2. Close Date
    3. Created Date
    """

    date_columns = []

    tentative_column = find_column(
        df,
        ["tentative", "close", "date"]
    )

    close_column = find_column(
        df,
        ["close", "date"]
    )

    created_column = find_column(
        df,
        ["created", "date"]
    )

    if tentative_column:
        date_columns.append(tentative_column)

    if close_column:
        date_columns.append(close_column)

    if created_column:
        date_columns.append(created_column)

    all_dates = []

    for column in date_columns:

        parsed = parse_dates(
            df[column]
        )

        all_dates.append(
            parsed.dropna()
        )

    if not all_dates:
        return None

    combined = pd.concat(
        all_dates
    )

    if combined.empty:
        return None

    return combined.max()


def get_period_bounds(
    df,
    period="all_time"
):
    """
    Calculate the date range for a requested period.

    For current_quarter, the quarter is based on
    the latest available business date in the data.

    This is important when Monday.com contains historical
    data that does not extend to today's actual date.
    """

    if period is None:
        period = "all_time"

    period = str(period).lower().strip()

    # ---------------------------------------------------------
    # All time
    # ---------------------------------------------------------

    if period in (
        "all_time",
        "all",
        "total"
    ):
        return None, None

    # ---------------------------------------------------------
    # Determine reference date
    # ---------------------------------------------------------

    latest_date = get_latest_data_date(
        df
    )

    if latest_date is None:

        latest_date = pd.Timestamp(
            datetime.now()
        )

    # ---------------------------------------------------------
    # Current quarter
    # ---------------------------------------------------------

    if period == "current_quarter":

        start = quarter_start(
            latest_date
        )

        end = quarter_end(
            latest_date
        )

        return start, end

    # ---------------------------------------------------------
    # Previous quarter
    # ---------------------------------------------------------

    if period == "previous_quarter":

        current_start = quarter_start(
            latest_date
        )

        end = (
            current_start
            - pd.Timedelta(days=1)
        )

        start = quarter_start(
            end
        )

        return start, end

    # ---------------------------------------------------------
    # Current year
    # ---------------------------------------------------------

    if period == "current_year":

        start = pd.Timestamp(
            year=latest_date.year,
            month=1,
            day=1
        )

        end = pd.Timestamp(
            year=latest_date.year,
            month=12,
            day=31
        )

        return start, end

    # ---------------------------------------------------------
    # Previous year
    # ---------------------------------------------------------

    if period == "previous_year":

        year = latest_date.year - 1

        start = pd.Timestamp(
            year=year,
            month=1,
            day=1
        )

        end = pd.Timestamp(
            year=year,
            month=12,
            day=31
        )

        return start, end

    # ---------------------------------------------------------
    # Unknown period
    # ---------------------------------------------------------

    return None, None


def filter_by_period(
    df,
    period,
    date_columns
):
    """
    Filter records using one or more date columns.

    A record is included when ANY valid date column falls
    inside the requested period.

    This prevents records from disappearing simply because
    Close Date is blank while Tentative Close Date exists.
    """

    if period in (
        None,
        "all_time",
        "all",
        "total"
    ):
        return df.copy(), 0

    start, end = get_period_bounds(
        df,
        period
    )

    if start is None or end is None:
        return df.copy(), 0

    masks = []

    valid_date_count = 0

    for column in date_columns:

        if column not in df.columns:
            continue

        dates = parse_dates(
            df[column]
        )

        valid_date_count += int(
            dates.notna().sum()
        )

        masks.append(
            dates.between(
                start,
                end,
                inclusive="both"
            )
        )

    if not masks:

        return df.iloc[0:0].copy(), len(df)

    combined_mask = masks[0]

    for mask in masks[1:]:

        combined_mask = (
            combined_mask
            | mask
        )

    filtered = df[
        combined_mask
    ].copy()

    invalid_count = int(
        len(df) - valid_date_count
    )

    return filtered, max(
        0,
        invalid_count
    )


# =============================================================
# PIPELINE SUMMARY
# =============================================================

def pipeline_summary(
    deals_df,
    sector=None,
    period="all_time"
):
    """
    Calculate pipeline KPIs from the Deals board.

    Current quarter is calculated using the latest
    available business date in the dataset.
    """

    if deals_df is None or deals_df.empty:

        return {
            "sector": sector or "All sectors",
            "period": period,
            "deal_count": 0,
            "pipeline_value": 0.0,
            "weighted_pipeline": 0.0,
            "status_distribution": {},
            "data_quality": {},
            "warnings": [],
            "message": "No deal data available."
        }

    df = deals_df.copy()

    # ---------------------------------------------------------
    # Identify columns
    # ---------------------------------------------------------

    sector_column = find_column(
        df,
        ["sector"]
    )

    value_column = find_column(
        df,
        ["deal", "value"]
    )

    status_column = find_column(
        df,
        ["deal", "status"]
    )

    probability_column = find_column(
        df,
        ["closure", "probability"]
    )

    tentative_close_column = find_column(
        df,
        ["tentative", "close", "date"]
    )

    close_column = find_column(
        df,
        ["close", "date"]
    )

    created_column = find_column(
        df,
        ["created", "date"]
    )

    warnings = []

    # ---------------------------------------------------------
    # Sector filter
    # ---------------------------------------------------------

    if sector and sector_column:

        requested_sector = (
            str(sector)
            .strip()
            .lower()
        )

        df = df[
            df[sector_column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            == requested_sector
        ].copy()

    # ---------------------------------------------------------
    # Date filtering
    # ---------------------------------------------------------

    date_columns = []

    if tentative_close_column:
        date_columns.append(
            tentative_close_column
        )

    if close_column:
        date_columns.append(
            close_column
        )

    if created_column:
        date_columns.append(
            created_column
        )

    original_count = len(df)

    if period not in (
        None,
        "all_time",
        "all",
        "total"
    ):

        start, end = get_period_bounds(
            df,
            period
        )

        if start is not None and end is not None:

            masks = []

            for column in date_columns:

                dates = parse_dates(
                    df[column]
                )

                masks.append(
                    dates.between(
                        start,
                        end,
                        inclusive="both"
                    )
                )

            if masks:

                combined_mask = masks[0]

                for mask in masks[1:]:
                    combined_mask = (
                        combined_mask
                        | mask
                    )

                df = df[
                    combined_mask
                ].copy()

                excluded = (
                    original_count
                    - len(df)
                )

                if excluded > 0:

                    warnings.append(
                        f"{excluded} record(s) "
                        f"were outside the "
                        f"{period} date range."
                    )

            else:

                warnings.append(
                    "No usable date columns "
                    "were available for "
                    "period filtering."
                )

    # ---------------------------------------------------------
    # No matching records
    # ---------------------------------------------------------

    if df.empty:

        return {
            "sector": sector or "All sectors",
            "period": period,
            "deal_count": 0,
            "pipeline_value": 0.0,
            "weighted_pipeline": 0.0,
            "status_distribution": {},
            "data_quality": {},
            "warnings": warnings,
            "message": "No matching deals found."
        }

    # ---------------------------------------------------------
    # Deal values
    # ---------------------------------------------------------

    if value_column:

        values = to_numeric(
            df[value_column]
        )

        pipeline_value = float(
            values.sum(
                skipna=True
            )
        )

        missing_values = int(
            values.isna().sum()
        )

        if missing_values > 0:

            warnings.append(
                f"{missing_values} deal(s) "
                f"have missing or invalid "
                f"Deal Value."
            )

    else:

        values = pd.Series(
            0.0,
            index=df.index
        )

        pipeline_value = 0.0

        missing_values = None

    # ---------------------------------------------------------
    # Weighted pipeline
    # ---------------------------------------------------------

    probability_map = {
        "high": 0.80,
        "medium": 0.50,
        "low": 0.20
    }

    if probability_column:

        probabilities = (
            df[probability_column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            .map(probability_map)
        )

        missing_probability = int(
            probabilities.isna().sum()
        )

        probabilities = (
            probabilities
            .fillna(0.0)
        )

        weighted_pipeline = float(
            (
                values.fillna(0.0)
                * probabilities
            ).sum()
        )

        if missing_probability > 0:

            warnings.append(
                f"{missing_probability} deal(s) "
                f"have missing or unrecognized "
                f"Closure Probability."
            )

    else:

        weighted_pipeline = 0.0

        missing_probability = None

    # ---------------------------------------------------------
    # Status distribution
    # ---------------------------------------------------------

    if status_column:

        status_distribution = (
            df[status_column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .replace("", "Unknown")
            .value_counts()
            .to_dict()
        )

    else:

        status_distribution = {}

    # ---------------------------------------------------------
    # Return
    # ---------------------------------------------------------

    return {
        "sector": sector or "All sectors",
        "period": period,
        "deal_count": int(len(df)),
        "pipeline_value": pipeline_value,
        "weighted_pipeline": weighted_pipeline,
        "status_distribution": status_distribution,
        "data_quality": {
            "missing_deal_values":
                missing_values,
            "missing_probability":
                missing_probability
        },
        "warnings": warnings
    }


# =============================================================
# SECTOR BREAKDOWN
# =============================================================

def sector_breakdown(
    deals_df,
    period="all_time"
):
    """
    Return pipeline value by sector.
    """

    if deals_df is None or deals_df.empty:
        return []

    df = deals_df.copy()

    sector_column = find_column(
        df,
        ["sector"]
    )

    value_column = find_column(
        df,
        ["deal", "value"]
    )

    if not sector_column:
        return []

    # ---------------------------------------------------------
    # Optional period filtering
    # ---------------------------------------------------------

    if period not in (
        None,
        "all_time",
        "all",
        "total"
    ):

        tentative_column = find_column(
            df,
            ["tentative", "close", "date"]
        )

        close_column = find_column(
            df,
            ["close", "date"]
        )

        created_column = find_column(
            df,
            ["created", "date"]
        )

        date_columns = []

        if tentative_column:
            date_columns.append(
                tentative_column
            )

        if close_column:
            date_columns.append(
                close_column
            )

        if created_column:
            date_columns.append(
                created_column
            )

        if date_columns:

            start, end = get_period_bounds(
                df,
                period
            )

            masks = []

            for column in date_columns:

                dates = parse_dates(
                    df[column]
                )

                masks.append(
                    dates.between(
                        start,
                        end,
                        inclusive="both"
                    )
                )

            if masks:

                mask = masks[0]

                for current_mask in masks[1:]:
                    mask = (
                        mask
                        | current_mask
                    )

                df = df[
                    mask
                ].copy()

    # ---------------------------------------------------------
    # Clean sector
    # ---------------------------------------------------------

    df["sector_clean"] = (
        df[sector_column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
    )

    # ---------------------------------------------------------
    # Calculate
    # ---------------------------------------------------------

    if value_column:

        df["value_numeric"] = to_numeric(
            df[value_column]
        )

        result = (
            df.groupby(
                "sector_clean"
            )
            .agg(
                deal_count=(
                    "sector_clean",
                    "size"
                ),
                pipeline_value=(
                    "value_numeric",
                    "sum"
                )
            )
            .reset_index()
            .sort_values(
                "pipeline_value",
                ascending=False
            )
        )

    else:

        result = (
            df["sector_clean"]
            .value_counts()
            .rename_axis(
                "sector_clean"
            )
            .reset_index(
                name="deal_count"
            )
        )

        result["pipeline_value"] = 0.0

    return result.to_dict(
        orient="records"
    )


# =============================================================
# AVAILABLE SECTORS
# =============================================================

def available_sectors(
    deals_df
):

    if deals_df is None or deals_df.empty:
        return []

    sector_column = find_column(
        deals_df,
        ["sector"]
    )

    if not sector_column:
        return []

    sectors = (
        deals_df[sector_column]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
        .tolist()
    )

    return sorted(
        sectors,
        key=lambda x: x.lower()
    )


# =============================================================
# REVENUE SUMMARY
# =============================================================

def revenue_summary(
    deals_df,
    work_orders_df,
    period="all_time"
):
    """
    Calculate revenue using Work Orders.

    Revenue:
    - Billed revenue
    - Collected revenue
    - Outstanding revenue

    Deal data is retained as pipeline context.
    """

    if work_orders_df is None:
        work_orders_df = pd.DataFrame()

    if deals_df is None:
        deals_df = pd.DataFrame()

    wo = work_orders_df.copy()

    # ---------------------------------------------------------
    # Work order columns
    # ---------------------------------------------------------

    billed_column = find_column(
        wo,
        ["billed", "value", "rupees"]
    )

    collected_column = find_column(
        wo,
        ["collected", "amount", "rupees"]
    )

    expected_column = find_column(
        wo,
        ["expected", "billing", "month"]
    )

    actual_billing_column = find_column(
        wo,
        ["actual", "billing", "month"]
    )

    # ---------------------------------------------------------
    # Date filter
    # ---------------------------------------------------------

    if period not in (
        None,
        "all_time",
        "all",
        "total"
    ):

        date_columns = []

        if expected_column:
            date_columns.append(
                expected_column
            )

        if actual_billing_column:
            date_columns.append(
                actual_billing_column
            )

        if date_columns:

            start, end = get_period_bounds(
                wo,
                period
            )

            masks = []

            for column in date_columns:

                dates = parse_dates(
                    wo[column]
                )

                masks.append(
                    dates.between(
                        start,
                        end,
                        inclusive="both"
                    )
                )

            if masks:

                mask = masks[0]

                for current_mask in masks[1:]:
                    mask = (
                        mask
                        | current_mask
                    )

                wo = wo[
                    mask
                ].copy()

    # ---------------------------------------------------------
    # Billed
    # ---------------------------------------------------------

    if billed_column:

        billed = to_numeric(
            wo[billed_column]
        )

        billed_revenue = float(
            billed.sum(
                skipna=True
            )
        )

        missing_billed = int(
            billed.isna().sum()
        )

    else:

        billed_revenue = 0.0
        missing_billed = None

    # ---------------------------------------------------------
    # Collected
    # ---------------------------------------------------------

    if collected_column:

        collected = to_numeric(
            wo[collected_column]
        )

        collected_revenue = float(
            collected.sum(
                skipna=True
            )
        )

        missing_collected = int(
            collected.isna().sum()
        )

    else:

        collected_revenue = 0.0
        missing_collected = None

    # ---------------------------------------------------------
    # Outstanding
    # ---------------------------------------------------------

    outstanding_revenue = (
        billed_revenue
        - collected_revenue
    )

    warnings = []

    if (
        missing_billed
        and missing_billed > 0
    ):

        warnings.append(
            f"{missing_billed} work order(s) "
            f"have missing or invalid "
            f"billed values."
        )

    if (
        missing_collected
        and missing_collected > 0
    ):

        warnings.append(
            f"{missing_collected} work order(s) "
            f"have missing or invalid "
            f"collected amounts."
        )

    # ---------------------------------------------------------
    # Deal pipeline context
    # ---------------------------------------------------------

    deal_pipeline_context = 0.0

    if not deals_df.empty:

        value_column = find_column(
            deals_df,
            ["deal", "value"]
        )

        if value_column:

            values = to_numeric(
                deals_df[value_column]
            )

            deal_pipeline_context = float(
                values.sum(
                    skipna=True
                )
            )

    return {
        "period": period,
        "work_order_count": int(
            len(wo)
        ),
        "billed_revenue": billed_revenue,
        "collected_revenue": collected_revenue,
        "outstanding_revenue": outstanding_revenue,
        "deal_pipeline_context": deal_pipeline_context,
        "data_quality": {
            "missing_revenue_values":
                missing_billed,
            "missing_collected_values":
                missing_collected
        },
        "warnings": warnings
    }


# =============================================================
# OPERATIONS SUMMARY
# =============================================================

def operations_summary(
    work_orders_df,
    period="all_time"
):
    """
    Summarize work-order operations.

    period is supported so the agent can safely pass
    the parsed time period.
    """

    if work_orders_df is None or work_orders_df.empty:

        return {
            "period": period,
            "work_order_count": 0,
            "status_distribution": {},
            "sector_distribution": {},
            "billing_status_distribution": {},
            "data_quality": {},
            "warnings": []
        }

    df = work_orders_df.copy()

    warnings = []

    # ---------------------------------------------------------
    # Identify columns
    # ---------------------------------------------------------

    execution_column = find_column(
        df,
        ["execution", "status"]
    )

    sector_column = find_column(
        df,
        ["sector"]
    )

    billing_column = find_column(
        df,
        ["billing", "status"]
    )

    # ---------------------------------------------------------
    # Period filtering
    # ---------------------------------------------------------

    if period not in (
        None,
        "all_time",
        "all",
        "total"
    ):

        date_columns = []

        for keywords in [
            ["actual", "billing", "month"],
            ["expected", "billing", "month"],
            ["data", "delivery", "date"],
            ["probable", "start", "date"],
            ["probable", "end", "date"]
        ]:

            column = find_column(
                df,
                keywords
            )

            if column:
                date_columns.append(
                    column
                )

        if date_columns:

            start, end = get_period_bounds(
                df,
                period
            )

            masks = []

            for column in date_columns:

                dates = parse_dates(
                    df[column]
                )

                masks.append(
                    dates.between(
                        start,
                        end,
                        inclusive="both"
                    )
                )

            if masks:

                mask = masks[0]

                for current_mask in masks[1:]:
                    mask = (
                        mask
                        | current_mask
                    )

                df = df[
                    mask
                ].copy()

    # ---------------------------------------------------------
    # Execution status
    # ---------------------------------------------------------

    if execution_column:

        execution_status = (
            df[execution_column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .replace("", "Unknown")
            .value_counts()
            .to_dict()
        )

        missing_execution = int(
            df[execution_column]
            .isna()
            .sum()
        )

    else:

        execution_status = {}
        missing_execution = None

    # ---------------------------------------------------------
    # Sector
    # ---------------------------------------------------------

    if sector_column:

        sector_distribution = (
            df[sector_column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .replace("", "Unknown")
            .value_counts()
            .to_dict()
        )

    else:

        sector_distribution = {}

    # ---------------------------------------------------------
    # Billing
    # ---------------------------------------------------------

    if billing_column:

        billing_status_distribution = (
            df[billing_column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .replace("", "Unknown")
            .value_counts()
            .to_dict()
        )

    else:

        billing_status_distribution = {}

    # ---------------------------------------------------------
    # Warnings
    # ---------------------------------------------------------

    if (
        missing_execution
        and missing_execution > 0
    ):

        warnings.append(
            f"{missing_execution} work order(s) "
            f"have missing execution status."
        )

    return {
        "period": period,
        "work_order_count": int(
            len(df)
        ),
        "status_distribution":
            execution_status,
        "sector_distribution":
            sector_distribution,
        "billing_status_distribution":
            billing_status_distribution,
        "data_quality": {
            "missing_execution_status":
                missing_execution
        },
        "warnings": warnings
    }


# =============================================================
# BILLING SUMMARY
# =============================================================

def billing_summary(
    work_orders_df,
    period="all_time"
):
    """
    Summarize billing activity.
    """

    if work_orders_df is None or work_orders_df.empty:

        return {
            "period": period,
            "work_order_count": 0,
            "billing_status_distribution": {},
            "billed_amount": 0.0,
            "collected_amount": 0.0,
            "outstanding_amount": 0.0,
            "data_quality": {},
            "warnings": []
        }

    df = work_orders_df.copy()

    warnings = []

    # ---------------------------------------------------------
    # Identify columns
    # ---------------------------------------------------------

    billing_status_column = find_column(
        df,
        ["billing", "status"]
    )

    billed_column = find_column(
        df,
        ["billed", "value", "rupees"]
    )

    collected_column = find_column(
        df,
        ["collected", "amount", "rupees"]
    )

    # ---------------------------------------------------------
    # Period filtering
    # ---------------------------------------------------------

    if period not in (
        None,
        "all_time",
        "all",
        "total"
    ):

        date_columns = []

        for keywords in [
            ["actual", "billing", "month"],
            ["expected", "billing", "month"],
            ["data", "delivery", "date"]
        ]:

            column = find_column(
                df,
                keywords
            )

            if column:
                date_columns.append(
                    column
                )

        if date_columns:

            start, end = get_period_bounds(
                df,
                period
            )

            masks = []

            for column in date_columns:

                dates = parse_dates(
                    df[column]
                )

                masks.append(
                    dates.between(
                        start,
                        end,
                        inclusive="both"
                    )
                )

            if masks:

                mask = masks[0]

                for current_mask in masks[1:]:
                    mask = (
                        mask
                        | current_mask
                    )

                df = df[
                    mask
                ].copy()

    # ---------------------------------------------------------
    # Billing statuses
    # ---------------------------------------------------------

    if billing_status_column:

        billing_distribution = (
            df[billing_status_column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .replace("", "Unknown")
            .value_counts()
            .to_dict()
        )

    else:

        billing_distribution = {}

    # ---------------------------------------------------------
    # Billed amount
    # ---------------------------------------------------------

    if billed_column:

        billed = to_numeric(
            df[billed_column]
        )

        billed_amount = float(
            billed.sum(
                skipna=True
            )
        )

        missing_billed = int(
            billed.isna().sum()
        )

    else:

        billed_amount = 0.0
        missing_billed = None

    # ---------------------------------------------------------
    # Collected amount
    # ---------------------------------------------------------

    if collected_column:

        collected = to_numeric(
            df[collected_column]
        )

        collected_amount = float(
            collected.sum(
                skipna=True
            )
        )

        missing_collected = int(
            collected.isna().sum()
        )

    else:

        collected_amount = 0.0
        missing_collected = None

    # ---------------------------------------------------------
    # Outstanding
    # ---------------------------------------------------------

    outstanding_amount = (
        billed_amount
        - collected_amount
    )

    if (
        missing_billed
        and missing_billed > 0
    ):

        warnings.append(
            f"{missing_billed} work order(s) "
            f"have missing or invalid billed values."
        )

    if (
        missing_collected
        and missing_collected > 0
    ):

        warnings.append(
            f"{missing_collected} work order(s) "
            f"have missing or invalid collected amounts."
        )

    return {
        "period": period,
        "work_order_count": int(
            len(df)
        ),
        "billing_status_distribution":
            billing_distribution,
        "billed_amount":
            billed_amount,
        "collected_amount":
            collected_amount,
        "outstanding_amount":
            outstanding_amount,
        "data_quality": {
            "missing_billed_values":
                missing_billed,
            "missing_collected_values":
                missing_collected
        },
        "warnings": warnings
    }