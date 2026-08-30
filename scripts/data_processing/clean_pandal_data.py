import pandas as pd
import re
from pathlib import Path


# --------------------------------------------------
# 1. File locations
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "raw" / "kolkata_durga_puja_complete_guide.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "pandals_cleaned.csv"


# --------------------------------------------------
# 2. Read the raw CSV
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("Raw records:", len(df))


# --------------------------------------------------
# 3. Clean column names
# --------------------------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)

print("Columns:")
print(df.columns.tolist())


# --------------------------------------------------
# 4. Clean distance
# --------------------------------------------------

def convert_distance_to_meters(value):
    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    number = re.search(r"\d+(?:\.\d+)?", value)

    if not number:
        return None

    number = float(number.group())

    if "km" in value:
        return round(number * 1000)

    return round(number)


df["distance_m"] = df["distance"].apply(
    convert_distance_to_meters
)


# --------------------------------------------------
# 5. Clean approximate time
# --------------------------------------------------

def convert_time_to_minutes(value):
    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    numbers = re.findall(r"\d+", value)

    if not numbers:
        return None

    numbers = [int(n) for n in numbers]

    # Example: "8-10 mins" -> average = 9
    return round(sum(numbers) / len(numbers))


df["approx_time_min"] = df["approx._time"].apply(
    convert_time_to_minutes
)


# --------------------------------------------------
# 6. Clean text fields
# --------------------------------------------------

text_columns = [
    "pandal_name",
    "nearest_metro_station",
    "area",
    "last_mile_transport",
    "google_maps_link"
]

for column in text_columns:
    df[column] = df[column].astype("string").str.strip()


# --------------------------------------------------
# 7. Remove duplicate pandals
# --------------------------------------------------

df = df.drop_duplicates(
    subset=["pandal_name"],
    keep="first"
)


# --------------------------------------------------
# 8. Keep useful columns
# --------------------------------------------------

df = df[
    [
        "pandal_name",
        "nearest_metro_station",
        "area",
        "last_mile_transport",
        "distance_m",
        "approx_time_min",
        "google_maps_link"
    ]
]


# --------------------------------------------------
# 9. Save processed data
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Cleaned records:", len(df))
print("Saved to:", OUTPUT_FILE)