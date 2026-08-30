from collections import deque
from pathlib import Path

import pandas as pd

from scripts.routing.metro_graph import build_metro_graph
from scripts.routing.route_options import build_route_options


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
# Data
# --------------------------------------------------

pandals = pd.read_csv(PANDAL_FILE)


# --------------------------------------------------
# Settings
# --------------------------------------------------

# Exact optimization is practical for a small number
# of selected pandals.
MAX_EXACT_PANDALS = 12


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
# Metro route
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
# First-leg cost
# Start station -> first pandal
# --------------------------------------------------

def calculate_first_leg_cost(
    start_station,
    pandal_name,
    graph
):

    pandal = get_pandal(pandal_name)

    if pandal is None:
        return None

    target_station = (
        pandal["nearest_metro_station"]
    )

    metro_route = find_metro_route(
        graph,
        start_station,
        target_station
    )

    if metro_route is None:
        return None

    metro_hops = len(metro_route) - 1

    last_mile_time = int(
        pandal["approx_time_min"]
    )

    # MVP estimate:
    # approximately 3 minutes per Metro hop.
    total_time = (
        metro_hops * 3
        + last_mile_time
    )

    return {
        "time_min": total_time,
        "metro_route": metro_route
    }


# --------------------------------------------------
# Pairwise travel cost
# --------------------------------------------------

def calculate_pair_cost(
    from_pandal,
    to_pandal
):

    result = build_route_options(
        from_pandal,
        to_pandal
    )

    if result is None:
        return None

    recommended_mode = result["recommended"]

    for option in result["options"]:

        if option["mode"] == recommended_mode:

            return {
                "time_min": option["time_min"],
                "recommended": recommended_mode,
                "options": result["options"]
            }

    return None


# --------------------------------------------------
# Build cost matrices
# --------------------------------------------------

def build_cost_matrices(
    start_station,
    selected_pandals
):

    graph = build_metro_graph()

    first_leg_costs = {}
    pair_costs = {}

    # ----------------------------------------------
    # Start -> every selected pandal
    # ----------------------------------------------

    for pandal in selected_pandals:

        cost = calculate_first_leg_cost(
            start_station,
            pandal,
            graph
        )

        first_leg_costs[pandal] = cost

    # ----------------------------------------------
    # Every pandal -> every other pandal
    # ----------------------------------------------

    for from_pandal in selected_pandals:

        pair_costs[from_pandal] = {}

        for to_pandal in selected_pandals:

            if from_pandal == to_pandal:
                continue

            pair_costs[from_pandal][to_pandal] = (
                calculate_pair_cost(
                    from_pandal,
                    to_pandal
                )
            )

    return first_leg_costs, pair_costs


# --------------------------------------------------
# Exact optimization using dynamic programming
# --------------------------------------------------

def optimize_exact(
    start_station,
    selected_pandals
):

    n = len(selected_pandals)

    first_leg_costs, pair_costs = (
        build_cost_matrices(
            start_station,
            selected_pandals
        )
    )

    # DP:
    #
    # (visited_mask, last_index)
    #
    # = minimum total time to visit exactly
    #   those pandals and finish at last_index.
    dp = {}

    parent = {}

    # ----------------------------------------------
    # Start with each possible first pandal
    # ----------------------------------------------

    for i, pandal in enumerate(
        selected_pandals
    ):

        first_cost = first_leg_costs.get(
            pandal
        )

        if first_cost is None:
            continue

        mask = 1 << i

        dp[(mask, i)] = first_cost["time_min"]

        parent[(mask, i)] = None

    # ----------------------------------------------
    # Build larger states
    # ----------------------------------------------

    for mask_size in range(1, n + 1):

        for (mask, last_index), current_cost in list(
            dp.items()
        ):

            if mask.bit_count() != mask_size:
                continue

            last_pandal = selected_pandals[
                last_index
            ]

            for next_index in range(n):

                if mask & (1 << next_index):
                    continue

                next_pandal = selected_pandals[
                    next_index
                ]

                pair_cost = pair_costs[
                    last_pandal
                ].get(next_pandal)

                if pair_cost is None:
                    continue

                new_mask = (
                    mask
                    | (1 << next_index)
                )

                new_cost = (
                    current_cost
                    + pair_cost["time_min"]
                )

                key = (
                    new_mask,
                    next_index
                )

                if (
                    key not in dp
                    or new_cost < dp[key]
                ):

                    dp[key] = new_cost

                    parent[key] = (
                        mask,
                        last_index
                    )

    # ----------------------------------------------
    # Find best complete state
    # ----------------------------------------------

    full_mask = (1 << n) - 1

    candidates = [
        (cost, last_index)
        for (
            mask,
            last_index
        ), cost in dp.items()
        if mask == full_mask
    ]

    if not candidates:
        return selected_pandals.copy()

    _, last_index = min(
        candidates,
        key=lambda item: item[0]
    )

    # ----------------------------------------------
    # Reconstruct route
    # ----------------------------------------------

    route_indices = []

    state = (
        full_mask,
        last_index
    )

    while state is not None:

        _, current_index = state

        route_indices.append(
            current_index
        )

        state = parent[state]

    route_indices.reverse()

    return [
        selected_pandals[index]
        for index in route_indices
    ]


# --------------------------------------------------
# Fast greedy fallback
# --------------------------------------------------

def optimize_greedy(
    start_station,
    selected_pandals
):

    graph = build_metro_graph()

    remaining = selected_pandals.copy()
    ordered = []

    current_station = start_station

    # ----------------------------------------------
    # Pick first pandal
    # ----------------------------------------------

    first_candidates = []

    for pandal in remaining:

        cost = calculate_first_leg_cost(
            start_station,
            pandal,
            graph
        )

        if cost is not None:

            first_candidates.append(
                (
                    cost["time_min"],
                    pandal
                )
            )

    if not first_candidates:
        return selected_pandals.copy()

    _, first = min(
        first_candidates,
        key=lambda item: item[0]
    )

    ordered.append(first)
    remaining.remove(first)

    # ----------------------------------------------
    # Pick nearest next pandal repeatedly
    # ----------------------------------------------

    current_pandal = first

    while remaining:

        candidates = []

        for pandal in remaining:

            cost = calculate_pair_cost(
                current_pandal,
                pandal
            )

            if cost is not None:

                candidates.append(
                    (
                        cost["time_min"],
                        pandal
                    )
                )

        if not candidates:
            ordered.extend(remaining)
            break

        _, next_pandal = min(
            candidates,
            key=lambda item: item[0]
        )

        ordered.append(next_pandal)

        remaining.remove(next_pandal)

        current_pandal = next_pandal

    return ordered


# --------------------------------------------------
# Public function
# --------------------------------------------------

def optimize_pandal_order(
    start_station,
    selected_pandals
):

    # Remove duplicate selections while preserving
    # the user's input.
    selected_pandals = list(
        dict.fromkeys(selected_pandals)
    )

    if len(selected_pandals) <= 1:
        return selected_pandals

    if len(selected_pandals) <= MAX_EXACT_PANDALS:

        return optimize_exact(
            start_station,
            selected_pandals
        )

    return optimize_greedy(
        start_station,
        selected_pandals
    )