import re


def extract_sector(question, available_sectors):
    """
    Try to identify a sector mentioned in the user's question.
    """

    question_lower = question.lower()

    # Exact sector matching first
    for sector in available_sectors:
        if sector.lower() in question_lower:
            return sector

    # Common variations
    aliases = {
        "renewable energy": "Renewables",
        "renewable": "Renewables",
        "power": "Powerline",
        "power lines": "Powerline",
    }

    for alias, sector in aliases.items():
        if alias in question_lower:
            return sector

    return None


def detect_time_period(question):
    """
    Identify the requested time period.
    """

    q = question.lower()

    if "this quarter" in q or "current quarter" in q:
        return "current_quarter"

    if "last quarter" in q:
        return "last_quarter"

    if "next quarter" in q:
        return "next_quarter"

    if "this year" in q or "current year" in q:
        return "current_year"

    if "last 30 days" in q:
        return "last_30_days"

    if "last month" in q:
        return "last_month"

    return "all_time"


def detect_intent(question):
    """
    Identify the type of business question.
    """

    q = question.lower()

    # --------------------------------
    # Sector comparison / ranking
    # --------------------------------

    if any(
        phrase in q
        for phrase in [
            "which sector",
            "what sector",
            "sector has",
            "sector-wise",
            "sector wise",
            "by sector",
            "compare sectors",
            "top sector",
            "best sector",
            "largest sector"
        ]
    ):
        return "sector_breakdown"

    # --------------------------------
    # Pipeline
    # --------------------------------

    if any(
        phrase in q
        for phrase in [
            "pipeline",
            "sales pipeline",
            "deal pipeline"
        ]
    ):
        return "pipeline_health"

    # --------------------------------
    # Revenue
    # --------------------------------

    if any(
        phrase in q
        for phrase in [
            "revenue",
            "deal value",
            "sales value",
            "sales revenue"
        ]
    ):
        return "revenue"

    # --------------------------------
    # Operations
    # --------------------------------

    if any(
        phrase in q
        for phrase in [
            "work order",
            "work orders",
            "operations",
            "operational",
            "execution",
            "projects"
        ]
    ):
        return "operations"

    # --------------------------------
    # Billing / collections
    # --------------------------------

    if any(
        phrase in q
        for phrase in [
            "billing",
            "billed",
            "invoice",
            "invoices",
            "receivable",
            "receivables",
            "collection",
            "collections"
        ]
    ):
        return "billing"

    # --------------------------------
    # General
    # --------------------------------

    return "general"

def parse_question(question, available_sectors):
    """
    Convert natural language into structured intent.
    """

    return {
        "original_question": question,
        "intent": detect_intent(question),
        "sector": extract_sector(
            question,
            available_sectors
        ),
        "time_period": detect_time_period(question)
    }