def build_journey_steps(
    start_station,
    metro_segments,
    pandal_name,
    last_mile_transport,
    last_mile_distance_m,
    last_mile_time_min,
    return_distance_m
):
    steps = []

    # ----------------------------------------
    # 1. Starting point
    # ----------------------------------------

    steps.append({
        "type": "start",
        "title": "Start",
        "station": start_station
    })

    # ----------------------------------------
    # 2. Metro segments
    # ----------------------------------------

    for index, segment in enumerate(metro_segments):

        if index > 0:
            steps.append({
                "type": "transfer",
                "title": "Change Metro Line",
                "station": segment["stations"][0]
            })

        steps.append({
            "type": "metro",
            "line": segment["line"],
            "stations": segment["stations"]
        })

    # ----------------------------------------
    # 3. Last-mile journey
    # ----------------------------------------

    steps.append({
        "type": "last_mile",
        "transport": last_mile_transport,
        "distance_m": last_mile_distance_m,
        "time_min": last_mile_time_min
    })

    # ----------------------------------------
    # 4. Pandal
    # ----------------------------------------

    steps.append({
        "type": "pandal",
        "name": pandal_name
    })

    # ----------------------------------------
    # 5. Return to Metro
    # ----------------------------------------

    steps.append({
        "type": "return_to_metro",
        "distance_m": return_distance_m
    })

    return steps