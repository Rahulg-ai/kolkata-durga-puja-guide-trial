from scripts.routing.route_options import build_route_options


tests = [
    (
        "Baghbazar Sarbojanin",
        "Sikdar Bagan"
    ),
    (
        "Baghbazar Sarbojanin",
        "College Square"
    ),
    (
        "College Square",
        "Ekdalia Evergreen"
    ),
]


for current, next_pandal in tests:

    result = build_route_options(
        current,
        next_pandal
    )

    print("\n==============================")
    print("FROM:", current)
    print("TO:", next_pandal)
    print("RECOMMENDED:", result["recommended"])

    print("\nOPTIONS:")

    for option in result["options"]:

        print(
            "-",
            option["mode"],
            "|",
            option["time_min"],
            "min"
        )