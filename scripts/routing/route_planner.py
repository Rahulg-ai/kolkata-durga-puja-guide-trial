from collections import deque
from pathlib import Path

import pandas as pd

from scripts.routing.metro_graph import build_metro_graph
from scripts.routing.route_segments import build_segments
from scripts.routing.route_options import build_route_options
from scripts.routing.route_optimizer import optimize_pandal_order


# --------------------------------------------------
# File paths
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
# Find a pandal by name
# --------------------------------------------------

def get_pandal(name):
    result = pandals[
        pandals["pandal_name"].str.lower() == name.lower()
    ]

    if result.empty:
        return None

    return result.iloc[0]


# --------------------------------------------------
# Find shortest Metro route using BFS
# --------------------------------------------------

def find_metro_route(graph, start, destination):

    queue = deque([[start]])
    visited = {start}

    while queue:
        path = queue.popleft()
        current_station = path[-1]

        if current_station == destination:
            return path

        for next_station in graph.get(current_station, []):

            if next_station not in visited:

                visited.add(next_station)

                queue.append(
                    path + [next_station]
                )

    return None


# --------------------------------------------------
# Choose the first pandal from the starting station
# --------------------------------------------------

def choose_first_pandal(
    start_station,
    remaining_pandals,
    graph
):

    best_pandal = None
    best_route = None
    best_score = float("inf")

    for pandal_name in remaining_pandals:

        pandal = get_pandal(pandal_name)

        if pandal is None:
            continue

        target_station = (
            pandal["nearest_metro_station"]
        )

        metro_route = find_metro_route(
            graph,
            start_station,
            target_station
        )

        if metro_route is None:
            continue

        metro_hops = len(metro_route) - 1

        last_mile_time = int(
            pandal["approx_time_min"]
        )

        score = (
            metro_hops * 3
            + last_mile_time
        )

        if score < best_score:

            best_score = score
            best_pandal = pandal
            best_route = metro_route

    return best_pandal, best_route


# --------------------------------------------------
# Choose the next pandal
# --------------------------------------------------

def choose_next_pandal(
    current_pandal_name,
    remaining_pandals
):

    best_pandal_name = None
    best_options = None
    best_score = float("inf")

    for pandal_name in remaining_pandals:

        options = build_route_options(
            current_pandal_name,
            pandal_name
        )

        if options is None:
            continue

        recommended_mode = options["recommended"]

        recommended_option = next(
            (
                option
                for option in options["options"]
                if option["mode"] == recommended_mode
            ),
            None
        )

        if recommended_option is None:
            continue

        score = recommended_option["time_min"]

        if score < best_score:

            best_score = score
            best_pandal_name = pandal_name
            best_options = options

    return best_pandal_name, best_options


# --------------------------------------------------
# Build complete Puja route
# --------------------------------------------------

def build_puja_route(
    start_station,
    selected_pandals
):

    graph = build_metro_graph()

    ordered_pandals = optimize_pandal_order(
        start_station,
        selected_pandals
    )
    remaining = ordered_pandals.copy()

    complete_route = []

    if not remaining:
        return []

    # --------------------------------------------------
    # FIRST PANDAL
    # --------------------------------------------------

    first_pandal, first_metro_route = (
        choose_first_pandal(
            start_station,
            remaining,
            graph
        )
    )

    if first_pandal is None:
        return []

    first_name = first_pandal["pandal_name"]

    first_metro_segments = build_segments(
        first_metro_route
    )

    complete_route.append({
        "pandal": first_name,
        "metro_station": (
            first_pandal["nearest_metro_station"]
        ),
        "metro_route": first_metro_route,
        "metro_segments": first_metro_segments,
        "last_mile_transport": (
            first_pandal["last_mile_transport"]
        ),
        "last_mile_distance_m": int(
            first_pandal["distance_m"]
        ),
        "last_mile_time_min": int(
            first_pandal["approx_time_min"]
        ),
        "google_maps_link": (
            first_pandal["google_maps_link"]
        ),
        "next_transition": None
    })

    remaining.remove(first_name)

    current_pandal_name = first_name

    # --------------------------------------------------
    # REMAINING PANDALS
    # --------------------------------------------------

    while remaining:

        next_pandal_name, _ = choose_next_pandal(
            current_pandal_name,
            remaining
        )

        if next_pandal_name is None:
            break

        next_pandal = get_pandal(
            next_pandal_name
        )

        if next_pandal is None:
            break

        # Find the actual Metro route to this pandal
        metro_route = find_metro_route(
            graph,
            current_pandal_name,
            next_pandal["nearest_metro_station"]
        )

        # We don't use this route directly here because
        # route_options.py decides whether Metro is useful.
        metro_segments = []

        if metro_route:
            metro_segments = build_segments(
                metro_route
            )

        complete_route.append({
            "pandal": next_pandal_name,
            "metro_station": (
                next_pandal["nearest_metro_station"]
            ),
            "metro_route": metro_route or [],
            "metro_segments": metro_segments,
            "last_mile_transport": (
                next_pandal["last_mile_transport"]
            ),
            "last_mile_distance_m": int(
                next_pandal["distance_m"]
            ),
            "last_mile_time_min": int(
                next_pandal["approx_time_min"]
            ),
            "google_maps_link": (
                next_pandal["google_maps_link"]
            ),
            "next_transition": None
        })

        remaining.remove(
            next_pandal_name
        )

        current_pandal_name = next_pandal_name

    # --------------------------------------------------
    # Add transition options between consecutive pandals
    # --------------------------------------------------

    for i in range(len(complete_route) - 1):

        current_pandal = complete_route[i]["pandal"]
        next_pandal = complete_route[i + 1]["pandal"]

        transition = build_route_options(
            current_pandal,
            next_pandal
        )

        complete_route[i]["next_transition"] = transition

    return complete_route