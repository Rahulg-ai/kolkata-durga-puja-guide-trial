from scripts.routing.route_optimizer import (
    optimize_pandal_order
)


selected = [
    "Ekdalia Evergreen",
    "Baghbazar Sarbojanin",
    "College Square",
    "Sikdar Bagan"
]


optimized = optimize_pandal_order(
    "Howrah",
    selected
)


print("\n===== OPTIMIZED ORDER =====\n")

for index, pandal in enumerate(
    optimized,
    start=1
):

    print(
        f"{index}. {pandal}"
    )