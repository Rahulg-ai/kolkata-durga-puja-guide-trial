from route_segments import build_segments


test_route = [
    "Howrah",
    "Mahakaran",
    "Esplanade",
    "Chandni Chowk",
    "Central",
    "M.G. Road",
    "Girish Park",
    "Shobhabazar Sutanuti",
    "Shyambazar"
]


segments = build_segments(test_route)


for segment in segments:

    print()
    print("LINE:", segment["line"])

    print(
        " → ".join(segment["stations"])
    )