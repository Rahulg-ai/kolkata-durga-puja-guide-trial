from collections import deque

from metro_graph import build_metro_graph


def find_route(graph, start, destination):

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

                new_path = path + [next_station]

                queue.append(new_path)

    return None


graph = build_metro_graph()

route = find_route(
    graph,
    "Howrah",
    "Kalighat"
)


print("Metro route:")

if route:

    for station in route:
        print("↓", station)

else:

    print("No route found.")