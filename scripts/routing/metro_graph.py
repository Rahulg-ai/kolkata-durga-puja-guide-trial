import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

METRO_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "metro_network_2026_cleaned.csv"
)


def normalize_station_name(name):
    """
    Convert different spellings of the same station
    into a common comparison format.
    """

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


def resolve_station_name(graph, station_name):
    """
    Return the actual station name used by the graph.

    Example:
    'MG Road' -> 'M.G. Road'
    """

    if station_name in graph:
        return station_name

    target = normalize_station_name(
        station_name
    )

    for graph_station in graph:

        if normalize_station_name(
            graph_station
        ) == target:

            return graph_station

    return None


def build_metro_graph():

    metro = pd.read_csv(
        METRO_FILE
    )

    graph = {}

    # Add all stations
    for station in metro["station_name"]:

        graph.setdefault(
            station,
            []
        )

    # Connect consecutive stations
    # on each Metro line
    for line, group in metro.groupby(
        "line"
    ):

        group = group.sort_values(
            "sequence"
        )

        stations = group[
            "station_name"
        ].tolist()

        for i in range(
            len(stations) - 1
        ):

            current_station = stations[i]
            next_station = stations[i + 1]

            if (
                next_station
                not in graph[current_station]
            ):

                graph[
                    current_station
                ].append(
                    next_station
                )

            if (
                current_station
                not in graph[next_station]
            ):

                graph[
                    next_station
                ].append(
                    current_station
                )

    return graph