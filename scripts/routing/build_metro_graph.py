import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. File path
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

METRO_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "metro_network_2026_cleaned.csv"
)


# --------------------------------------------------
# 2. Read Metro data
# --------------------------------------------------

metro = pd.read_csv(METRO_FILE)

print("Metro records:", len(metro))


# --------------------------------------------------
# 3. Create the graph
# --------------------------------------------------

graph = {}


def add_station(station):
    """Create an empty station entry if it doesn't exist."""
    if station not in graph:
        graph[station] = []


def add_connection(station_a, station_b, line, connection_type):
    """Add a connection between two stations."""
    graph[station_a].append({
        "station": station_b,
        "line": line,
        "type": connection_type
    })

    graph[station_b].append({
        "station": station_a,
        "line": line,
        "type": connection_type
    })


# --------------------------------------------------
# 4. Add all stations
# --------------------------------------------------

for station in metro["station_name"]:
    add_station(station)


# --------------------------------------------------
# 5. Connect consecutive stations on each line
# --------------------------------------------------

for line, group in metro.groupby("line"):

    group = group.sort_values("sequence")

    stations = group["station_name"].tolist()

    for i in range(len(stations) - 1):

        station_a = stations[i]
        station_b = stations[i + 1]

        add_connection(
            station_a,
            station_b,
            line,
            "metro"
        )


# --------------------------------------------------
# 6. Add interchange connections
# --------------------------------------------------

station_groups = (
    metro.groupby("station_name")["line"]
    .unique()
)

for station, lines in station_groups.items():

    if len(lines) > 1:

        # Store the transfer information
        graph[station].append({
            "station": station,
            "line": "INTERCHANGE",
            "type": "transfer"
        })


# --------------------------------------------------
# 7. Display some information
# --------------------------------------------------

print("\nTotal stations:", len(graph))

print("\nExample connections:")

for station in [
    "Howrah",
    "Esplanade",
    "Park Street",
    "Kalighat"
]:

    print(f"\n{station}:")

    for connection in graph.get(station, []):
        print(connection)