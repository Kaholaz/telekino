from models import Node, Connection, Point, Route
import random


def create_random_nodes(
    number_of_nodes: int, endpoints: int, domain: tuple[float, float] = (-20, 20)
):
    """
    Create a list of random nodes.
    """
    r = random.Random(42)
    points = [
        Point(
            r.random() * (domain[1] - domain[0]) + domain[0],
            r.random() * (domain[1] - domain[0]) + domain[0],
        )
        for _ in range(number_of_nodes)
    ]
    return create_nodes(points, endpoints)


def create_nodes(
    points: list[Point], endpoints: int
) -> tuple[list[Node], list[Connection]]:
    """
    Initialize the nodes and connections between them based on the given points.
    The first node is the source and the last node is the sink.
    """
    nodes = [Node(i, points[i], {}) for i in range(len(points))]
    connections = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            connection = Connection((nodes[i], nodes[j]), 0)
            connection.update_cost()
            connections.append(connection)

            nodes[i].connections[j] = connection
            nodes[j].connections[i] = connection

    for node in nodes[:endpoints]:
        node.make_endpoint()

    return nodes, connections


def get_value(node: Node):
    connected_nodes = {route.source for route in node.endpoints.values()}
    return sum(
        node.connections[connected_node].calculate_cost()
        for connected_node in connected_nodes
    )


def find_move_direction(node: Node, wiggle=0.01):
    """
    Find the direction in which the node should move to minimize the cost from
    one of the node to the other nodes it is connected to.
    """
    if len(node.endpoints) < 2:
        return Point(0, 0)

    # The value is the sum of the cost from the source to the sink and the cost to the drain.
    current_value = get_value(node)

    # How does the value change if we move the node a little bit in the x or y direction?
    node.pos.x += wiggle
    new_value = get_value(node)
    dx = -(new_value - current_value)

    node.pos.x -= wiggle
    node.pos.y += wiggle
    new_value = get_value(node)
    dy = -(new_value - current_value)

    node.pos.y -= wiggle
    return Point(dx, dy)


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    nodes, connections = create_random_nodes(20, 3)
    colors = [
        "red",
        "green",
        "blue",
        "yellow",
        "orange",
        "purple",
        "pink",
        "brown",
        "gray",
    ]
    for node in filter(lambda n: n.endpoint, nodes):
        plt.plot(node.pos.x, node.pos.y, "o", color=colors[node.id % len(colors)])
        plt.text(node.pos.x + 1, node.pos.y, f"endpoint {node.id}")

    for _ in range(500):
        for node in nodes:
            plt.plot(node.pos.x, node.pos.y, "o", color=colors[node.id % len(colors)], markersize=1)
            node.send_routes()

        directions = {
            node.id: find_move_direction(node) for node in nodes if not node.endpoint
        }
        for node in nodes:
            if node.endpoint:
                continue

            direction = directions[node.id]
            plt.arrow(node.pos.x, node.pos.y, 3 * direction.x, 3 * direction.y)
            node.pos.x += direction.x
            node.pos.y += direction.y

        for connection in connections:
            connection.update_cost()

    for node in filter(lambda n: not n.endpoint, nodes):
        for route in node.endpoints.values():
            connection = node.connections[route.source]
            strength = 1 / connection.calculate_cost()
            plt.plot(
                [n.pos.x for n in connection.nodes],
                [n.pos.y for n in connection.nodes], 
                color="black",
                alpha=strength,
            )


    plt.show()
