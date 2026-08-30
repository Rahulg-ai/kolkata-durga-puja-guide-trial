import pandas as pd
from pathlib import Path


# ----------------------------------------
# 1. File locations
# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "raw" / "kolkata_metro_network_data.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "metro_stations_cleaned.csv"


# ----------------------------------------
# 2. Read the raw Metro CSV
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
    .str.replace("/", "_")
)


# ----------------------------------------
# 4. Clean text values
# ----------------------------------------

df["line"] = df["line"].astype("string").str.strip()
df["station_name"] = df["station_name"].astype("string").str.strip()
df["interchange___notes"] = (
    df["interchange___notes"]
    .fillna("")
    .astype("string")
    .str.strip()
)


# ----------------------------------------
# 5. Make sequence numeric
# ----------------------------------------

df["sequence"] = pd.to_numeric(
    df["sequence"],
    errors="coerce"
)

df = df.dropna(subset=["sequence"])

df["sequence"] = df["sequence"].astype(int)


# ----------------------------------------
# 6. Remove duplicate station records
# ----------------------------------------

df = df.drop_duplicates(
    subset=["line", "station_name"],
    keep="first"
)


# ----------------------------------------
# 7. Sort Metro stations
# ----------------------------------------

df = df.sort_values(
    by=["line", "sequence"]
)


# ----------------------------------------
# 8. Save processed data
# ----------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Cleaned Metro records:", len(df))
print("Saved to:", OUTPUT_FILE)