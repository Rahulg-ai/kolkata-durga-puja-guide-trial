import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

METRO_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "metro_network_2026_cleaned.csv"
)


metro = pd.read_csv(METRO_FILE)


def find_line_between(station_a, station_b):
    """
    Find the Metro line connecting two consecutive stations.
    """

    for line, group in metro.groupby("line"):

        group = group.sort_values("sequence")
        stations = group["station_name"].tolist()

        for i in range(len(stations) - 1):

            first = stations[i]
            second = stations[i + 1]

            if (
                (first == station_a and second == station_b)
                or
                (first == station_b and second == station_a)
            ):
                return line

    return None


def build_segments(station_route):
    """
    Convert a list of Metro stations into
    line-based journey segments.
    """

    if not station_route or len(station_route) < 2:
        return []

    segments = []

    current_line = None
    current_stations = []

    for i in range(len(station_route) - 1):

        station_a = station_route[i]
        station_b = station_route[i + 1]

        line = find_line_between(
            station_a,
            station_b
        )

        if line is None:
            continue

        # First Metro connection
        if current_line is None:

            current_line = line
            current_stations = [
                station_a,
                station_b
            ]

        # Same line continues
        elif line == current_line:

            current_stations.append(station_b)

        # Line changes
        else:

            segments.append({
                "line": current_line,
                "stations": current_stations
            })

            current_line = line

            current_stations = [
                station_a,
                station_b
            ]

    # Add the final segment
    if current_line is not None:

        segments.append({
            "line": current_line,
            "stations": current_stations
        })

    return segments