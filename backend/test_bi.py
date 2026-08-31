from monday_client import (
    get_board_items,
    DEALS_BOARD_ID
)

from data_processor import (
    monday_items_to_dataframe,
    process_deals
)

from bi_engine import (
    pipeline_summary,
    sector_breakdown,
    available_sectors
)


# Get live data
raw = get_board_items(DEALS_BOARD_ID)

# Convert to DataFrame
df = monday_items_to_dataframe(raw)

# Clean data
deals, warnings = process_deals(df)


print("\n==============================")
print("AVAILABLE SECTORS")
print("==============================")

for sector in available_sectors(deals):
    print("-", sector)


print("\n==============================")
print("RENEWABLES PIPELINE")
print("==============================")

result = pipeline_summary(
    deals,
    sector="Renewables"
)

print(result)


print("\n==============================")
print("SECTOR BREAKDOWN")
print("==============================")

breakdown = sector_breakdown(deals)

for row in breakdown:
    print(row)