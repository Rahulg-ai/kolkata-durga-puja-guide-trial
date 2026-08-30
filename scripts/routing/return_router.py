from collections import deque
from pathlib import Path

import pandas as pd

from scripts.routing.metro_graph import (
    build_metro_graph,
    resolve_station_name,
)


BASE_DIR = Path(__file__).resolve().parents[2]


PANDAL_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "pandals_with_coordinates.csv"
)


METRO_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "metro_network_2026_cleaned.csv"
)


pandals = pd.read_csv(PANDAL_FILE)

metro = pd.read_csv(METRO_FILE)


# =========================================================
# BASIC HELPERS
# =========================================================

def get_pandal(name):
    result = pandals[
        pandals["pandal_name"]
        .astype(str)
        .str.lower()
        == str(name).lower()
    ]

    if result.empty:
        return None

    return result.iloc[0]


def find_metro_route(
    graph,
    start_station,
    destination_station,
):
    start_station = resolve_station_name(
        graph,
        start_station,
    )

    destination_station = resolve_station_name(
        graph,
        destination_station,
    )

    if (
        start_station is None
        or destination_station is None
    ):
        return None

    if start_station == destination_station:
        return [start_station]

    queue = deque(
        [[start_station]]
    )

    visited = {
        start_station
    }

    while queue:

        path = queue.popleft()

        current = path[-1]

        if current == destination_station:
            return path

        for next_station in graph.get(
            current,
            [],
        ):

            if next_station not in visited:

                visited.add(
                    next_station
                )

                queue.append(
                    path + [next_station]
                )

    return None


# =========================================================
# METRO LINE LOOKUP
# =========================================================

def get_station_lines(station_name):
    """
    Return all Metro lines on which a station appears.
    """

    station_name = str(
        station_name
    ).strip().lower()

    matches = metro[
        metro["station_name"]
        .astype(str)
        .str.strip()
        .str.lower()
        == station_name
    ]

    if matches.empty:
        return []

    return (
        matches["line"]
        .astype(str)
        .drop_duplicates()
        .tolist()
    )


def get_edge_line(
    from_station,
    to_station,
):
    """
    Determine which Metro line connects
    two consecutive stations.
    """

    from_station = str(
        from_station
    ).strip().lower()

    to_station = str(
        to_station
    ).strip().lower()

    from_rows = metro[
        metro["station_name"]
        .astype(str)
        .str.strip()
        .str.lower()
        == from_station
    ]

    if from_rows.empty:
        return None

    for _, row in from_rows.iterrows():

        line = row["line"]

        sequence = row.get(
            "sequence"
        )

        if pd.isna(sequence):
            continue

        same_line = metro[
            metro["line"]
            .astype(str)
            == str(line)
        ].copy()

        same_line = same_line.sort_values(
            "sequence"
        )

        stations = (
            same_line[
                "station_name"
            ]
            .astype(str)
            .tolist()
        )

        lowered = [
            station.strip().lower()
            for station in stations
        ]

        try:
            from_index = lowered.index(
                from_station
            )
            to_index = lowered.index(
                to_station
            )
        except ValueError:
            continue

        if abs(
            from_index - to_index
        ) == 1:

            return str(line)

    return None


# =========================================================
# BUILD METRO SEGMENTS
# =========================================================

def build_metro_segments(
    metro_route,
):
    """
    Convert:

        A → B → C → D → E

    into:

        Blue Line
        A → B → C

        Green Line
        C → D → E

    and identify interchange stations.
    """

    if not metro_route:
        return [], []

    if len(metro_route) == 1:
        return (
            [
                {
                    "line": None,
                    "stations": metro_route,
                }
            ],
            [],
        )

    edge_lines = []

    for index in range(
        len(metro_route) - 1
    ):

        current_station = (
            metro_route[index]
        )

        next_station = (
            metro_route[index + 1]
        )

        line = get_edge_line(
            current_station,
            next_station,
        )

        edge_lines.append(line)


    # -----------------------------------------------------
    # Fallback if a line could not be detected
    # -----------------------------------------------------

    cleaned_lines = []

    previous_line = None

    for line in edge_lines:

        if line is None:
            line = previous_line

        if line is None:
            line = "Metro"

        cleaned_lines.append(
            line
        )

        previous_line = line


    # -----------------------------------------------------
    # Build segments
    # -----------------------------------------------------

    segments = []

    current_line = cleaned_lines[0]

    current_stations = [
        metro_route[0]
    ]


    for index, line in enumerate(
        cleaned_lines
    ):

        next_station = (
            metro_route[index + 1]
        )


        if line == current_line:

            current_stations.append(
                next_station
            )

        else:

            segments.append(
                {
                    "line": current_line,
                    "stations": current_stations,
                }
            )

            current_line = line

            # Keep interchange station as the
            # first station of the new segment.
            current_stations = [
                metro_route[index],
                next_station,
            ]


    segments.append(
        {
            "line": current_line,
            "stations": current_stations,
        }
    )


    # -----------------------------------------------------
    # Identify interchanges
    # -----------------------------------------------------

    interchanges = []

    for index in range(
        1,
        len(segments),
    ):

        previous_segment = (
            segments[index - 1]
        )

        current_segment = (
            segments[index]
        )

        interchange_station = (
            current_segment[
                "stations"
            ][0]
        )

        interchanges.append(
            {
                "station":
                    interchange_station,

                "from_line":
                    previous_segment[
                        "line"
                    ],

                "to_line":
                    current_segment[
                        "line"
                    ],
            }
        )


    return segments, interchanges


# =========================================================
# LAST-MILE TRANSPORT
# =========================================================

def estimate_last_mile(
    distance_m,
    base_time_min,
):
    """
    Choose a sensible last-mile mode.

    Short distance:
        Walk

    Medium distance:
        Walk is still reasonable,
        but Auto is also offered.

    Long distance:
        Auto is recommended.

    The supplied base_time_min is retained as
    the fallback walking estimate.
    """

    distance_m = float(
        distance_m
    )

    base_time_min = float(
        base_time_min
    )


    # -----------------------------------------------------
    # Short walk
    # -----------------------------------------------------

    if distance_m <= 1000:

        walk_time = max(
            1,
            round(base_time_min)
        )

        auto_time = max(
            1,
            round(
                distance_m / 250
            )
        )

        return {
            "recommended":
                "Walk",

            "transport":
                "Walk",

            "walk_time_min":
                walk_time,

            "auto_time_min":
                auto_time,
        }


    # -----------------------------------------------------
    # Medium distance
    # -----------------------------------------------------

    if distance_m <= 2000:

        walk_time = max(
            1,
            round(base_time_min)
        )

        auto_time = max(
            2,
            round(
                distance_m / 250
            )
        )

        return {
            "recommended":
                "Auto",

            "transport":
                "Auto",

            "walk_time_min":
                walk_time,

            "auto_time_min":
                auto_time,
        }


    # -----------------------------------------------------
    # Long distance
    # -----------------------------------------------------

    auto_time = max(
        5,
        round(
            distance_m / 250
        )
    )


    walk_time = max(
        1,
        round(base_time_min)
    )


    return {
        "recommended":
            "Auto",

        "transport":
            "Auto",

        "walk_time_min":
            walk_time,

        "auto_time_min":
            auto_time,
    }


# =========================================================
# RETURN ROUTE
# =========================================================

def build_return_route(
    current_pandal_name,
    starting_station,
):

    pandal = get_pandal(
        current_pandal_name
    )

    if pandal is None:
        return None


    graph = build_metro_graph()


    current_metro = resolve_station_name(
        graph,
        pandal[
            "nearest_metro_station"
        ],
    )


    destination = resolve_station_name(
        graph,
        starting_station,
    )


    if (
        current_metro is None
        or destination is None
    ):
        return None


    metro_route = find_metro_route(
        graph,
        current_metro,
        destination,
    )


    if metro_route is None:
        return None


    # =====================================================
    # LAST MILE
    # =====================================================

    departure_distance = int(
        float(
            pandal["distance_m"]
        )
    )


    departure_time = int(
        float(
            pandal["approx_time_min"]
        )
    )


    last_mile = estimate_last_mile(
        departure_distance,
        departure_time,
    )


    # =====================================================
    # METRO
    # =====================================================

    metro_hops = max(
        0,
        len(metro_route) - 1
    )


    metro_time = (
        metro_hops * 3
    )


    total_time = (
        (
            last_mile[
                "auto_time_min"
            ]
            if last_mile[
                "recommended"
            ]
            == "Auto"
            else last_mile[
                "walk_time_min"
            ]
        )
        + metro_time
    )


    # =====================================================
    # LINE SEGMENTS
    # =====================================================

    metro_segments, interchanges = (
        build_metro_segments(
            metro_route
        )
    )


    # =====================================================
    # RESULT
    # =====================================================

    return {

        "from_pandal":
            current_pandal_name,

        "starting_station":
            destination,

        "nearest_metro_station":
            current_metro,

        "last_mile_transport":
            last_mile[
                "transport"
            ],

        "last_mile_recommended":
            last_mile[
                "recommended"
            ],

        "walk_to_metro_distance_m":
            departure_distance,

        "walk_to_metro_time_min":
            last_mile[
                "walk_time_min"
            ],

        "auto_to_metro_time_min":
            last_mile[
                "auto_time_min"
            ],

        "metro_route":
            metro_route,

        "metro_segments":
            metro_segments,

        "interchanges":
            interchanges,

        "metro_hops":
            metro_hops,

        "metro_time_min":
            metro_time,

        "estimated_time_min":
            total_time,
    }