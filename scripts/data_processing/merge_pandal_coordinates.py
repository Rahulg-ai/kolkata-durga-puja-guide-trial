import pandas as pd
import re
from pathlib import Path


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

PANDAL_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "pandal_metro_mapping.csv"
)

COORDINATE_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "kolkata_durga_puja_metro_guide.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "pandals_with_coordinates.csv"
)


# --------------------------------------------------
# 2. Read files
# --------------------------------------------------

pandals = pd.read_csv(PANDAL_FILE)
coordinates = pd.read_csv(COORDINATE_FILE)

print("Pandal records:", len(pandals))
print("Coordinate records:", len(coordinates))


# --------------------------------------------------
# 3. Normalize names
# --------------------------------------------------

def normalize_name(name):
    if pd.isna(name):
        return ""

    name = str(name).lower().strip()

    # Remove punctuation
    name = re.sub(r"[^a-z0-9\s]", "", name)

    # Normalize spaces
    name = re.sub(r"\s+", " ", name)

    return name


# --------------------------------------------------
# 4. Known safe name aliases
# --------------------------------------------------

NAME_ALIASES = {
    "sikdar bagan": "sikdar bagan sadharan",
    "kumartuli sarbojanin": "kumartuli sarbojonin",
    "mohammad ali park": "muhammad ali park",
    "mudiali": "mudiali club",
    "shib mandir": "shib mandir sarbojonin",
    "vivekananda park": "vivekananda park athletic club",
}
COORDINATE_OVERRIDES = {
    "dakshinpara": (22.612, 88.394),
    "dumdum park bharat chakra": (22.615, 88.406),
    "jatin das park": (22.523, 88.347),
    "23 pally": (22.522, 88.345),
}

# --------------------------------------------------
# 5. Create matching names
# --------------------------------------------------

pandals["match_name"] = (
    pandals["pandal_name"]
    .apply(normalize_name)
    .replace(NAME_ALIASES)
)

coordinates["match_name"] = (
    coordinates["Pandal Name"]
    .apply(normalize_name)
)


# --------------------------------------------------
# 6. Keep coordinate data
# --------------------------------------------------

coordinate_data = coordinates[
    [
        "match_name",
        "Coordinates"
    ]
].copy()


# --------------------------------------------------
# 7. Merge
# --------------------------------------------------

merged = pandals.merge(
    coordinate_data,
    on="match_name",
    how="left"
)


# --------------------------------------------------
# 8. Extract latitude and longitude
# --------------------------------------------------

def extract_coordinates(value):

    if pd.isna(value):
        return pd.Series([None, None])

    numbers = re.findall(
        r"-?\d+(?:\.\d+)?",
        str(value)
    )

    if len(numbers) < 2:
        return pd.Series([None, None])

    latitude = float(numbers[0])
    longitude = float(numbers[1])

    return pd.Series([
        latitude,
        longitude
    ])


merged[
    ["latitude", "longitude"]
] = merged["Coordinates"].apply(
    extract_coordinates
)
for index, row in merged.iterrows():

    key = normalize_name(row["pandal_name"])

    if key in COORDINATE_OVERRIDES:

        latitude, longitude = COORDINATE_OVERRIDES[key]

        merged.at[index, "latitude"] = latitude
        merged.at[index, "longitude"] = longitude

# --------------------------------------------------
# 9. Remove temporary columns
# --------------------------------------------------

merged = merged.drop(
    columns=[
        "match_name",
        "Coordinates"
    ]
)


# --------------------------------------------------
# 10. Check missing coordinates
# --------------------------------------------------

missing = merged[
    merged["latitude"].isna()
    | merged["longitude"].isna()
]

print("\nMissing coordinates:", len(missing))

if not missing.empty:

    print("\nPandal names needing review:")

    for name in missing["pandal_name"]:
        print("-", name)


# --------------------------------------------------
# 11. Save
# --------------------------------------------------

merged.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSaved:", OUTPUT_FILE)