import math
from collections import deque
from pathlib import Path

import pandas as pd

from scripts.routing.metro_graph import (
    build_metro_graph,
    resolve_station_name,
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

PANDAL_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "pandals_with_coordinates.csv"
)


# --------------------------------------------------
# Load pandal data
# --------------------------------------------------

pandals = pd.read_csv(PANDAL_FILE)


# --------------------------------------------------
# MVP settings
# --------------------------------------------------

# Direct walking is considered a good option up to
# this straight-line distance.
MAX_WALK_DISTANCE_M = 2500

# Under this distance, walking is the default
# recommendation.
WALK_RECOMMENDATION_LIMIT_M = 800

# Approximate walking speed.
WALKING_SPEED_M_PER_MIN = 80

# Rough auto estimate for MVP only.
AUTO_SPEED_M_PER_MIN = 250


# --------------------------------------------------
# Find pandal
# --------------------------------------------------

def get_pandal(name):

    result = pandals[
        pandals["pandal_name"].str.lower() == name.lower()
    ]

    if result.empty:
        return None

    return result.iloc[0]


# --------------------------------------------------
# Haversine distance
# --------------------------------------------------

def haversine_distance(
    latitude_1,
    longitude_1,
    latitude_2,
    longitude_2
):

    earth_radius_m = 6_371_000

    lat1 = math.radians(latitude_1)
    lat2 = math.radians(latitude_2)

    delta_lat = math.radians(
        latitude_2 - latitude_1
    )

    delta_lon = math.radians(
        longitude_2 - longitude_1
    )

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius_m * c


# --------------------------------------------------
# Find Metro route
# --------------------------------------------------

def find_metro_route(
    graph,
    start,
    destination
):

    start = resolve_station_name(
        graph,
        start
    )

    destination = resolve_station_name(
        graph,
        destination
    )

    if (
        start is None
        or destination is None
    ):
        return None

    queue = deque([[start]])
    visited = {start}

    while queue:

        path = queue.popleft()

        current_station = path[-1]

        if current_station == destination:
            return path

        for next_station in graph.get(
            current_station,
            []
        ):

            if next_station not in visited:

                visited.add(next_station)

                queue.append(
                    path + [next_station]
                )

    return None


# --------------------------------------------------
# Direct walking option
# --------------------------------------------------

def build_walk_option(
    current_pandal,
    next_pandal
):

    distance = haversine_distance(
        current_pandal["latitude"],
        current_pandal["longitude"],
        next_pandal["latitude"],
        next_pandal["longitude"]
    )

    distance = round(distance)

    if distance > MAX_WALK_DISTANCE_M:
        return None

    time_min = max(
        1,
        math.ceil(
            distance
            / WALKING_SPEED_M_PER_MIN
        )
    )

    return {
        "mode": "walk",
        "distance_m": distance,
        "time_min": time_min
    }


# --------------------------------------------------
# Direct Auto option
# --------------------------------------------------

def build_auto_option(
    current_pandal,
    next_pandal
):

    distance = haversine_distance(
        current_pandal["latitude"],
        current_pandal["longitude"],
        next_pandal["latitude"],
        next_pandal["longitude"]
    )

    distance = round(distance)

    time_min = max(
        1,
        math.ceil(
            distance
            / AUTO_SPEED_M_PER_MIN
        )
    )

    return {
        "mode": "auto",
        "distance_m": distance,
        "time_min": time_min,
        "estimated": True
    }


# --------------------------------------------------
# Metro option
# --------------------------------------------------

def build_metro_option(
    current_pandal,
    next_pandal,
    graph
):

    current_station = resolve_station_name(
        graph,
        current_pandal["nearest_metro_station"]
    )

    next_station = resolve_station_name(
        graph,
        next_pandal["nearest_metro_station"]
    )

    if (
        current_station is None
        or next_station is None
    ):
        return None

    # Same station = no Metro journey.
    if current_station == next_station:
        return None

    metro_route = find_metro_route(
        graph,
        current_station,
        next_station
    )

    if metro_route is None:
        return None

    # ...keep the rest of your existing function...

    departure_distance = int(
        current_pandal["distance_m"]
    )

    arrival_distance = int(
        next_pandal["distance_m"]
    )

    metro_hops = len(metro_route) - 1

    # Very rough MVP estimate.
    metro_time = metro_hops * 3

    departure_time = int(
        current_pandal["approx_time_min"]
    )

    arrival_time = int(
        next_pandal["approx_time_min"]
    )

    total_time = (
        departure_time
        + metro_time
        + arrival_time
    )

    return {
        "mode": "metro",
        "metro_route": metro_route,
        "departure_distance_m": departure_distance,
        "arrival_distance_m": arrival_distance,
        "metro_hops": metro_hops,
        "time_min": total_time,
        "estimated": True
    }


# --------------------------------------------------
# Build all route options
# --------------------------------------------------

def build_route_options(
    current_pandal_name,
    next_pandal_name
):

    current_pandal = get_pandal(
        current_pandal_name
    )

    next_pandal = get_pandal(
        next_pandal_name
    )

    if (
        current_pandal is None
        or next_pandal is None
    ):
        return None

    graph = build_metro_graph()

    options = []

    # WALK
    walk_option = build_walk_option(
        current_pandal,
        next_pandal
    )

    if walk_option:
        options.append(walk_option)

    # METRO
    metro_option = build_metro_option(
        current_pandal,
        next_pandal,
        graph
    )

    if metro_option:
        options.append(metro_option)

    # AUTO
    auto_option = build_auto_option(
        current_pandal,
        next_pandal
    )

    options.append(auto_option)

    # --------------------------------------------------
    # Recommendation
    # --------------------------------------------------

    recommended = None

    # Prefer walking for short distances.
    for option in options:

        if (
            option["mode"] == "walk"
            and option["distance_m"]
            <= WALK_RECOMMENDATION_LIMIT_M
        ):

            recommended = "walk"
            break

    # Otherwise choose the fastest estimated option.
    if recommended is None:

        recommended = min(
            options,
            key=lambda option: option["time_min"]
        )["mode"]

    return {
        "from": current_pandal_name,
        "to": next_pandal_name,
        "recommended": recommended,
        "options": options
    }