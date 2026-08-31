import os
import requests
from dotenv import load_dotenv

load_dotenv()


MONDAY_API_URL = "https://api.monday.com/v2"

MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
print("Token loaded:", bool(MONDAY_API_TOKEN))
print("Token length:", len(MONDAY_API_TOKEN) if MONDAY_API_TOKEN else 0)
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")


def monday_request(query, variables=None):
    headers = {
        "Authorization": MONDAY_API_TOKEN,
        "Content-Type": "application/json"
    }

    response = requests.post(
        MONDAY_API_URL,
        json={
            "query": query,
            "variables": variables or {}
        },
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    if "errors" in result:
        raise Exception(result["errors"])

    return result["data"]


def get_board_columns(board_id):
    query = """
    query ($board_id: [ID!]) {
        boards(ids: $board_id) {
            id
            name
            columns {
                id
                title
                type
            }
        }
    }
    """

    return monday_request(
        query,
        {"board_id": [board_id]}
    )


def get_board_items(board_id):
    all_items = []
    cursor = None

    query = """
    query ($board_id: [ID!], $cursor: String) {
        boards(ids: $board_id) {
            id
            name

            columns {
                id
                title
                type
            }

            items_page(
                limit: 100
                cursor: $cursor
            ) {
                cursor

                items {
                    id
                    name

                    column_values {
                        id
                        text
                        value
                        type
                    }
                }
            }
        }
    }
    """

    while True:

        data = monday_request(
            query,
            {
                "board_id": [board_id],
                "cursor": cursor
            }
        )

        board = data["boards"][0]

        page = board["items_page"]

        all_items.extend(page["items"])

        cursor = page.get("cursor")

        if not cursor:
            break

        # Continue fetching pages
        # until Monday returns no cursor.

    return {
        "boards": [
            {
                "id": board["id"],
                "name": board["name"],
                "columns": board["columns"],
                "items_page": {
                    "items": all_items
                }
            }
        ]
    }

if __name__ == "__main__":
    print("Testing Deals board...")
    print(get_board_columns(DEALS_BOARD_ID))

    print("\nTesting Work Orders board...")
    print(get_board_columns(WORK_ORDERS_BOARD_ID))

    print("\nFetching Deals...")
    print(get_board_items(DEALS_BOARD_ID))

    print("\nFetching Work Orders...")
    print(get_board_items(WORK_ORDERS_BOARD_ID))