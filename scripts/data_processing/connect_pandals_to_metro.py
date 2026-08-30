import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

PANDAL_FILE = BASE_DIR / "data" / "processed" / "pandals_cleaned.csv"
METRO_FILE = BASE_DIR / "data" / "processed" / "metro_stations_cleaned.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "pandal_metro_mapping.csv"


# --------------------------------------------------
# 2. Read the processed files
# --------------------------------------------------

pandals = pd.read_csv(PANDAL_FILE)
metro = pd.read_csv(METRO_FILE)

print("Pandals loaded:", len(pandals))
print("Metro records loaded:", len(metro))


# --------------------------------------------------
# 3. Normalize station names
# --------------------------------------------------

def normalize_station_name(name):
    if pd.isna(name):
        return ""

    name = str(name).strip().lower()

    replacements = {
        "m.g. road": "mg road",
        "m.g road": "mg road",
        "mg. road": "mg road",
        "netaji bhavan": "netaji bhawan",
    }

    return replacements.get(name, name)


# Create a common station key
metro["station_key"] = metro["station_name"].apply(
    normalize_station_name
)

pandals["station_key"] = pandals["nearest_metro_station"].apply(
    normalize_station_name
)


# --------------------------------------------------
# 4. Create station → Metro line mapping
# --------------------------------------------------

station_to_line = (
    metro
    .groupby("station_key")["line"]
    .apply(list)
    .to_dict()
)


# --------------------------------------------------
# 5. Find Metro line for each pandal
# --------------------------------------------------

def get_metro_lines(station):
    key = normalize_station_name(station)

    lines = station_to_line.get(key, [])

    if not lines:
        return "Unknown"

    return ", ".join(lines)


pandals["metro_line"] = pandals["nearest_metro_station"].apply(
    get_metro_lines
)


# --------------------------------------------------
# 6. Remove temporary column
# --------------------------------------------------

pandals = pandals.drop(columns=["station_key"])


# --------------------------------------------------
# 7. Save the final mapping
# --------------------------------------------------

pandals.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Saved:", OUTPUT_FILE)

# Show the Metro line counts
print("\nMetro line counts:")
print(pandals["metro_line"].value_counts(dropna=False))