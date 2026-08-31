def format_currency(value):
    """
    Convert numeric value into Indian currency format.
    """

    if value is None:
        return "₹0"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "₹0"

    if abs(value) >= 10000000:
        return f"₹{value / 10000000:.2f} Cr"

    if abs(value) >= 100000:
        return f"₹{value / 100000:.2f} L"

    if abs(value) >= 1000:
        return f"₹{value / 1000:.2f} K"

    return f"₹{value:,.2f}"


def format_pipeline(data):
    """
    Convert pipeline result into a readable business answer.
    """

    if not data:
        return "No pipeline data available."

    sector = data.get(
        "sector",
        "All sectors"
    )

    period = data.get(
        "period",
        "all_time"
    )

    deal_count = data.get(
        "deal_count",
        0
    )

    pipeline_value = data.get(
        "pipeline_value",
        0
    )

    weighted_pipeline = data.get(
        "weighted_pipeline",
        0
    )

    status_distribution = data.get(
        "status_distribution",
        {}
    )

    lines = []

    lines.append(
        f"Pipeline for {sector}"
    )

    lines.append(
        f"Period: {period}"
    )

    lines.append(
        f"Deals: {deal_count}"
    )

    lines.append(
        f"Pipeline value: {format_currency(pipeline_value)}"
    )

    lines.append(
        f"Weighted pipeline: {format_currency(weighted_pipeline)}"
    )

    if status_distribution:

        status_text = ", ".join(
            f"{status}: {count}"
            for status, count
            in status_distribution.items()
        )

        lines.append(
            f"Status: {status_text}"
        )

    warnings = data.get(
        "warnings",
        []
    )

    if warnings:
        lines.append("")
        lines.append("Data quality notes:")

        for warning in warnings[:5]:
            lines.append(
                f"- {warning}"
            )

    return "\n".join(lines)


def format_sector_breakdown(data):
    """
    Format sector breakdown and identify
    the largest pipeline sector.
    """

    if not data:
        return "No sector data available."

    largest = data[0]

    largest_sector = largest.get(
        "sector_clean",
        "Unknown"
    )

    largest_value = largest.get(
        "pipeline_value",
        0
    )

    largest_count = largest.get(
        "deal_count",
        0
    )

    lines = []

    lines.append(
        "Largest pipeline sector"
    )

    lines.append(
        f"Sector: {largest_sector}"
    )

    lines.append(
        f"Pipeline: {format_currency(largest_value)}"
    )

    lines.append(
        f"Deals: {largest_count}"
    )

    lines.append("")

    lines.append(
        "Sector breakdown:"
    )

    for row in data:

        sector = row.get(
            "sector_clean",
            "Unknown"
        )

        value = row.get(
            "pipeline_value",
            0
        )

        count = row.get(
            "deal_count",
            0
        )

        lines.append(
            f"- {sector}: "
            f"{format_currency(value)} "
            f"({count} deals)"
        )

    return "\n".join(lines)


def format_revenue(data):
    """
    Format revenue summary.
    """

    if not data:
        return "No revenue data available."

    period = data.get(
        "period",
        "all_time"
    )

    billed = data.get(
        "billed_revenue",
        0
    )

    collected = data.get(
        "collected_revenue",
        0
    )

    outstanding = data.get(
        "outstanding_revenue",
        0
    )

    work_orders = data.get(
        "work_order_count",
        0
    )

    lines = []

    lines.append(
        "Revenue Summary"
    )

    lines.append(
        f"Period: {period}"
    )

    lines.append(
        f"Work orders: {work_orders}"
    )

    lines.append(
        f"Billed revenue: {format_currency(billed)}"
    )

    lines.append(
        f"Collected revenue: {format_currency(collected)}"
    )

    lines.append(
        f"Outstanding revenue: "
        f"{format_currency(outstanding)}"
    )

    return "\n".join(lines)


def format_operations(data):
    """
    Format work-order operations summary.
    """

    if not data:
        return "No operations data available."

    period = data.get(
        "period",
        "all_time"
    )

    work_order_count = data.get(
        "work_order_count",
        0
    )

    status_distribution = data.get(
        "status_distribution",
        {}
    )

    sector_distribution = data.get(
        "sector_distribution",
        {}
    )

    billing_distribution = data.get(
        "billing_status_distribution",
        {}
    )

    lines = []

    lines.append(
        "Operations Summary"
    )

    lines.append(
        f"Period: {period}"
    )

    lines.append(
        f"Work orders: {work_order_count}"
    )

    if status_distribution:

        lines.append("")
        lines.append(
            "Execution status:"
        )

        for status, count in status_distribution.items():

            lines.append(
                f"- {status}: {count}"
            )

    if sector_distribution:

        lines.append("")
        lines.append(
            "Work orders by sector:"
        )

        for sector, count in sector_distribution.items():

            lines.append(
                f"- {sector}: {count}"
            )

    if billing_distribution:

        lines.append("")
        lines.append(
            "Billing status:"
        )

        for status, count in billing_distribution.items():

            lines.append(
                f"- {status}: {count}"
            )

    return "\n".join(lines)


def format_billing(data):
    """
    Format billing summary.
    """

    if not data:
        return "No billing data available."

    period = data.get(
        "period",
        "all_time"
    )

    billed = data.get(
        "billed_amount",
        data.get(
            "billed_revenue",
            0
        )
    )

    collected = data.get(
        "collected_amount",
        data.get(
            "collected_revenue",
            0
        )
    )

    outstanding = data.get(
        "outstanding_amount",
        data.get(
            "outstanding_revenue",
            0
        )
    )

    lines = []

    lines.append(
        "Billing Summary"
    )

    lines.append(
        f"Period: {period}"
    )

    lines.append(
        f"Billed: {format_currency(billed)}"
    )

    lines.append(
        f"Collected: {format_currency(collected)}"
    )

    lines.append(
        f"Outstanding: {format_currency(outstanding)}"
    )

    return "\n".join(lines)


def format_general():
    """
    Format fallback response.
    """

    return (
        "I understand the question, "
        "but I need a more specific "
        "business metric to analyze."
    )


def format_answer(answer_type, data):
    """
    Main formatter used by the BI agent.
    """

    if answer_type == "pipeline":

        return format_pipeline(data)

    if answer_type == "sector_breakdown":

        return format_sector_breakdown(data)

    if answer_type == "revenue":

        return format_revenue(data)

    if answer_type == "operations":

        return format_operations(data)

    if answer_type == "billing":

        return format_billing(data)

    return format_general()