from backend.monday_client import (
    get_board_items,
    DEALS_BOARD_ID,
    WORK_ORDERS_BOARD_ID
)

from backend.data_processor import (
    monday_items_to_dataframe,
    process_deals,
    process_work_orders
)

from backend.bi_engine import (
    pipeline_summary,
    sector_breakdown,
    available_sectors,
    revenue_summary,
    operations_summary,
    billing_summary
)

from backend.query_engine import parse_question
from backend.response_formatter import format_answer


class BusinessIntelligenceAgent:

    def __init__(self):
        self.deals = None
        self.work_orders = None

        self.deal_warnings = []
        self.work_order_warnings = []

    # =========================================================
    # LOAD DATA
    # =========================================================

    def load_data(self):
        """
        Retrieve fresh data from Monday.com
        and process both boards.
        """

        # =====================================================
        # DEALS
        # =====================================================

        raw_deals = get_board_items(
            DEALS_BOARD_ID
        )

        deals_df = monday_items_to_dataframe(
            raw_deals
        )

        (
            self.deals,
            self.deal_warnings
        ) = process_deals(
            deals_df
        )

        # =====================================================
        # WORK ORDERS
        # =====================================================

        raw_work_orders = get_board_items(
            WORK_ORDERS_BOARD_ID
        )

        work_orders_df = monday_items_to_dataframe(
            raw_work_orders
        )

        (
            self.work_orders,
            self.work_order_warnings
        ) = process_work_orders(
            work_orders_df
        )

    # =========================================================
    # ANSWER QUESTION
    # =========================================================

    def answer(self, question):
        """
        Understand the user's question,
        calculate the requested business metric,
        and return both structured data and
        a human-readable answer.
        """

        # =====================================================
        # REFRESH DATA
        # =====================================================

        self.load_data()

        # =====================================================
        # AVAILABLE SECTORS
        # =====================================================

        sectors = available_sectors(
            self.deals
        )

        # =====================================================
        # PARSE QUESTION
        # =====================================================

        intent = parse_question(
            question,
            sectors
        )

        intent_type = intent.get(
            "intent"
        )

        sector = intent.get(
            "sector"
        )

        period = intent.get(
            "time_period",
            "all_time"
        )

        # =====================================================
        # PIPELINE
        # =====================================================

        if intent_type == "pipeline_health":

            result = pipeline_summary(
                self.deals,
                sector=sector,
                period=period
            )

            # Add processing warnings
            if self.deal_warnings:

                result.setdefault(
                    "warnings",
                    []
                )

                result["warnings"].extend(
                    self.deal_warnings
                )

            # Human-readable answer
            answer = format_answer(
                "pipeline",
                result
            )

            return {
                "question": question,
                "intent": intent,
                "answer_type": "pipeline",
                "answer": answer,
                "data": result
            }

        # =====================================================
        # SECTOR BREAKDOWN
        # =====================================================

        if intent_type == "sector_breakdown":

            result = sector_breakdown(
                self.deals
            )

            # Human-readable answer
            answer = format_answer(
                "sector_breakdown",
                result
            )

            return {
                "question": question,
                "intent": intent,
                "answer_type": "sector_breakdown",
                "answer": answer,
                "data": result,
                "warnings": self.deal_warnings
            }

        # =====================================================
        # REVENUE
        # =====================================================

        if intent_type == "revenue":

            result = revenue_summary(
                self.deals,
                self.work_orders,
                period=period
            )

            # Human-readable answer
            answer = format_answer(
                "revenue",
                result
            )

            return {
                "question": question,
                "intent": intent,
                "answer_type": "revenue",
                "answer": answer,
                "data": result
            }

        # =====================================================
        # OPERATIONS
        # =====================================================

        if intent_type == "operations":

            # IMPORTANT:
            # operations_summary() currently accepts
            # only work_orders.
            #
            # Do NOT pass period here because that
            # previously caused:
            #
            # TypeError:
            # operations_summary() got an unexpected
            # keyword argument 'period'

            result = operations_summary(
                self.work_orders
            )

            # Human-readable answer
            answer = format_answer(
                "operations",
                result
            )

            return {
                "question": question,
                "intent": intent,
                "answer_type": "operations",
                "answer": answer,
                "data": result,
                "warnings": self.work_order_warnings
            }

        # =====================================================
        # BILLING
        # =====================================================

        if intent_type == "billing":

            # IMPORTANT:
            # billing_summary() currently accepts
            # only work_orders.
            #
            # Do NOT pass period unless you later
            # modify billing_summary itself.

            result = billing_summary(
                self.work_orders
            )

            # Human-readable answer
            answer = format_answer(
                "billing",
                result
            )

            return {
                "question": question,
                "intent": intent,
                "answer_type": "billing",
                "answer": answer,
                "data": result,
                "warnings": self.work_order_warnings
            }

        # =====================================================
        # GENERAL
        # =====================================================

        answer = format_answer(
            "general",
            {}
        )

        return {
            "question": question,
            "intent": intent,
            "answer_type": "general",
            "answer": answer,
            "message": answer
        }


# =============================================================
# DIRECT TEST
# =============================================================

if __name__ == "__main__":

    agent = BusinessIntelligenceAgent()

    questions = [
        "How's our pipeline looking for renewables this quarter?",
        "Which sector has the largest pipeline?",
        "How much revenue do we have?",
        "Show me our work orders",
        "What is happening with billing?",
        "Give me a business summary"
    ]

    for question in questions:

        print("\n")
        print("=" * 60)
        print("QUESTION")
        print("=" * 60)
        print(question)

        try:

            result = agent.answer(
                question
            )

            print("\nANSWER")
            print("=" * 60)
            print(result.get("answer"))

            print("\nSTRUCTURED DATA")
            print("=" * 60)
            print(result.get("data"))

            if result.get("warnings"):

                print("\nWARNINGS")
                print("=" * 60)

                for warning in result["warnings"]:
                    print(
                        f"- {warning}"
                    )

        except Exception as e:

            print("\nERROR")
            print("=" * 60)
            print(type(e).__name__)
            print(str(e))