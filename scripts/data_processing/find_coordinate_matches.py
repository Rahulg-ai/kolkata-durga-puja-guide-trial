import pandas as pd
import re
from pathlib import Path
from difflib import SequenceMatcher


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


def normalize_name(name):
    if pd.isna(name):
        return ""

    name = str(name).lower().strip()

    name = re.sub(
        r"[^a-z0-9\s]",
        "",
        name
    )

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name


pandals = pd.read_csv(PANDAL_FILE)
coordinates = pd.read_csv(COORDINATE_FILE)

pandals["match_name"] = (
    pandals["pandal_name"]
    .apply(normalize_name)
)

coordinates["match_name"] = (
    coordinates["Pandal Name"]
    .apply(normalize_name)
)


coordinate_names = (
    coordinates["match_name"]
    .dropna()
    .unique()
)


for _, pandal in pandals.iterrows():

    name = pandal["pandal_name"]
    normalized = pandal["match_name"]

    exact_match = normalized in coordinate_names

    if exact_match:
        continue

    best_match = None
    best_score = 0

    for candidate in coordinate_names:

        score = SequenceMatcher(
            None,
            normalized,
            candidate
        ).ratio()

        if score > best_score:
            best_score = score
            best_match = candidate

    print()
    print("Pandal:", name)
    print(
        "Best coordinate match:",
        best_match
    )
    print(
        "Similarity:",
        round(best_score * 100, 1),
        "%"
    )