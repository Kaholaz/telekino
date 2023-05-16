from models import Node, Connection, Point
from math import sqrt
from value_evaluator import update_distances

def create_nodes(points: list[Point]):
    nodes = [Node(i, points[i], {}) for i in range(len(points))]
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            distance = sqrt((points[i].x - points[j].x) ** 2 + (points[i].y - points[j].y) ** 2)
            connection = Connection((nodes[i], nodes[j]), distance)
            nodes[i].connections[j] = connection
            nodes[j].connections[i] = connection
    return nodes

def update_position(node: Node, new_pos):
    node.pos = new_pos
    for connection in node.connections.values():
        connection.distance = sqrt((connection.nodes[0].pos.x - connection.nodes[1].pos.x) ** 2 + (connection.nodes[0].pos.y - connection.nodes[1].pos.y) ** 2)

def find_move_direction(node: Node, nodes: list[Node], wiggle = 0.01):
    update_distances(nodes[0], nodes[-1])
    current_value = node.connections[node.sink.next_node.id].cost + \
        + node.connections[node.drain.next_node.id].cost
    current_pos = node.pos

    update_position(node, Point(node.pos.x + wiggle, node.pos.y))
    new_value = node.connections[node.sink.next_node.id].cost + \
        + node.connections[node.drain.next_node.id].cost
    dx = -(new_value - current_value)

    update_position(node, Point(node.pos.x - wiggle, node.pos.y + wiggle))
    new_value = node.connections[node.sink.next_node.id].cost + \
        + node.connections[node.drain.next_node.id].cost
    dy = -(new_value - current_value)

    update_position(node, current_pos)
    return Point(dx, dy)

if __name__ == "__main__":
    from matplotlib import pyplot as plt
    nodes = create_nodes([Point(5, -1), Point(0, -2), Point(2, 4), Point(-1, 3), Point(-3, 5)])

    for _ in range(500):
        if _ == 26:
            print("hi")
        for node in nodes:
            plt.plot(node.pos.x, node.pos.y, "o")

        directions = {node.id: find_move_direction(node, nodes) for node in nodes[1: -1]}
        for node in nodes[1:-1]:
            direction = directions[node.id]
            plt.arrow(node.pos.x, node.pos.y, 3 * direction.x, 3 * direction.y)

        for node in nodes[1:-1]:
            direction = directions[node.id]
            update_position(node, Point(node.pos.x + direction.x, node.pos.y + direction.y))
    plt.show()







