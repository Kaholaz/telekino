from models import Node, Connection, Point, Route


def create_nodes(points: list[Point]) -> tuple[list[Node], list[Connection]]:
    nodes = [Node(i, points[i], {}) for i in range(len(points))]
    connections = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            connection = Connection((nodes[i], nodes[j]), 0)
            connection.update_cost()
            connections.append(connection)

            nodes[i].connections[j] = connection
            nodes[j].connections[i] = connection

    nodes[0].sink = Route(nodes[0].id, 0)
    nodes[-1].drain = Route(nodes[-1].id, 0)

    return nodes, connections


def find_move_direction(node: Node, wiggle=0.01):
    if node.sink is None or node.drain is None:
        return Point(0, 0)

    current_value = (
        node.connections[node.sink.source].cost
        + node.connections[node.drain.source].cost
    )

    node.pos.x += wiggle
    new_value = (
        node.connections[node.sink.source].calculate_cost()
        + node.connections[node.drain.source].calculate_cost()
    )
    dx = -(new_value - current_value)

    node.pos.x -= wiggle
    node.pos.y += wiggle
    new_value = (
        node.connections[node.sink.source].calculate_cost()
        + node.connections[node.drain.source].calculate_cost()
    )
    dy = -(new_value - current_value)

    node.pos.y -= wiggle
    return Point(dx, dy)


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    nodes, connections = create_nodes(
        [Point(5, -1), Point(0, -2), Point(2, 4), Point(-1, 3), Point(-3, 5)]
    )

    for _ in range(500):
        for node in nodes:
            plt.plot(node.pos.x, node.pos.y, "o")
            node.send_routes()

        directions = {node.id: find_move_direction(node) for node in nodes[1:-1]}
        for node in nodes[1:-1]:
            direction = directions[node.id]
            plt.arrow(node.pos.x, node.pos.y, 3 * direction.x, 3 * direction.y)
            node.pos.x += direction.x
            node.pos.y += direction.y

        for connection in connections:
            connection.update_cost()

    plt.show()
