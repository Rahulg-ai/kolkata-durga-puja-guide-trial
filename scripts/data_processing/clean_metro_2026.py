import pandas as pd
from pathlib import Path


# ----------------------------------------
# 1. Project paths
# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "raw" / "metro_network_2026.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "metro_network_2026_cleaned.csv"


# ----------------------------------------
# 2. Read the CSV
# ----------------------------------------

df = pd.read_csv(INPUT_FILE)

print("Raw Metro records:", len(df))


# ----------------------------------------
# 3. Clean column names
# ----------------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)


# ----------------------------------------
# 4. Clean values
# ----------------------------------------

df["line"] = df["line"].astype("string").str.strip()
df["station_name"] = df["station_name"].astype("string").str.strip()

df["sequence"] = pd.to_numeric(
    df["sequence"],
    errors="coerce"
)

df = df.dropna(subset=["sequence"])

df["sequence"] = df["sequence"].astype(int)


# ----------------------------------------
# 5. Remove duplicates
# ----------------------------------------

df = df.drop_duplicates(
    subset=["line", "station_name"],
    keep="first"
)


# ----------------------------------------
# 6. Sort the network
# ----------------------------------------

df = df.sort_values(
    by=["line", "sequence"]
).reset_index(drop=True)


# ----------------------------------------
# 7. Save cleaned data
# ----------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Cleaned Metro records:", len(df))
print("Saved to:", OUTPUT_FILE)


# ----------------------------------------
# 8. Show line counts
# ----------------------------------------

print("\nStations by line:")
print(df["line"].value_counts())


# ----------------------------------------
# 9. Find interchange stations
# ----------------------------------------

interchanges = (
    df.groupby("station_name")["line"]
    .unique()
)

interchanges = interchanges[
    interchanges.apply(len) > 1
]

print("\nInterchange stations:")

if len(interchanges) == 0:
    print("None found")
else:
    for station, lines in interchanges.items():
        print(f"{station}: {', '.join(lines)}")