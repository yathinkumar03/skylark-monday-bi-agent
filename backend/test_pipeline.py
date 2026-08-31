from monday_client import (
    get_board_items,
    DEALS_BOARD_ID,
    WORK_ORDERS_BOARD_ID,
)

from data_processor import (
    monday_items_to_dataframe,
    process_deals,
    process_work_orders,
)


print("\n==============================")
print("DEALS")
print("==============================")

deals_raw = get_board_items(DEALS_BOARD_ID)

deals_df = monday_items_to_dataframe(deals_raw)

deals_clean, deals_warnings = process_deals(deals_df)

print("\nRows:", len(deals_clean))
print("Columns:", len(deals_clean.columns))

print("\nSample:")
print(deals_clean.head(3).to_string())

print("\nData quality warnings:")
for warning in deals_warnings[:10]:
    print("-", warning)


print("\n==============================")
print("WORK ORDERS")
print("==============================")

work_raw = get_board_items(WORK_ORDERS_BOARD_ID)

work_df = monday_items_to_dataframe(work_raw)

work_clean, work_warnings = process_work_orders(work_df)

print("\nRows:", len(work_clean))
print("Columns:", len(work_clean.columns))

print("\nSample:")
print(work_clean.head(3).to_string())

print("\nData quality warnings:")
for warning in work_warnings[:10]:
    print("-", warning)