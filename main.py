from argparse import ArgumentParser, Namespace
from models import Node, Connection, Point
import random
import argparse

colors = [
    "red",
    "green",
    "blue",
    "orange",
    "purple",
    "pink",
    "brown",
    "gray",
    "black",
    "cyan",
    "magenta",
]


def create_random_nodes(
    number_of_nodes: int,
    endpoints: int,
    seed: int | None = None,
    node_domain: tuple[float, float] = (-20, 20),
    endpoint_domain: tuple[float, float] | None = None,
):
    """
    Create a list of random nodes.
    """
    if node_domain[0] > node_domain[1]:
        raise ValueError(
            "The first element of node_domain must be less than the second."
        )
    if endpoint_domain is not None and endpoint_domain[0] > endpoint_domain[1]:
        raise ValueError(
            "The first element of endpoint_domain must be less than the second."
        )

    random.seed(seed)
    points = [
        Point(
            random.uniform(*node_domain),
            random.uniform(*node_domain),
        )
        for _ in range(number_of_nodes)
    ]

    nodes, connections = create_nodes(points, endpoints)

    if endpoint_domain is not None:
        for node in filter(lambda n: n.endpoint, nodes):
            node.pos = Point(
                random.uniform(*endpoint_domain),
                random.uniform(*endpoint_domain),
            )

            for connection in node.connections.values():
                connection.update_cost()

    return nodes, connections


def create_nodes(
    points: list[Point], endpoints: int
) -> tuple[list[Node], list[Connection]]:
    """
    Initialize the nodes and connections between them based on the given points.
    The first node is the source and the last node is the sink.
    """

    if args.number_of_endpoints > args.number_of_nodes:
        raise ValueError(
            "The number of endpoints cannot be greater than the number of nodes."
        )

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
    """
    Compute the nodes worth based on the cost from all routes to the connected endpoints.
    """

    connected_nodes = {route.source for route in node.endpoint_routes.values()}
    return -sum(
        node.connections[connected_node].calculate_cost()
        for connected_node in connected_nodes
    ) * len(connected_nodes)


def find_move_direction(node: Node, wiggle: float, move_strength: float):
    """
    Find the direction in which the node should move to minimize the cost from
    one of the node to the other nodes it is connected to.
    """

    # Do not move if the node only knows about one route to an endpoint.
    if len(node.endpoint_routes) < 2:
        return Point(0, 0)

    # The value is the sum of the cost from the source to the sink and the cost to the drain.
    current_value = get_value(node)

    # How does the value change if we move the node a little bit in the x or y direction?
    node.pos.x += wiggle
    new_value = get_value(node)
    dx = new_value - current_value

    node.pos.x -= wiggle
    node.pos.y += wiggle
    new_value = get_value(node)
    dy = new_value - current_value

    node.pos.y -= wiggle
    return Point(dx / wiggle * move_strength, dy / wiggle * move_strength)


def simulate(
    simulation_steps: int = 1000,
    wiggle: float = 0.01,
    move_strength: float = 0.01,
    number_of_nodes: int = 5,
    number_of_endpoints: int = 2,
    seed: int | None = None,
    transmit_from_endpoints: bool = False,
    node_domain: tuple[float, float] = (-20, 20),
    endpoint_domain: tuple[float, float] = None,
    draw_steps: bool = True,
):
    """

    Simulate the network. The nodes will move around to minimize the cost to the endpoints.

    Args:
        simulation_steps (int, optional): number of steps to simulate. Defaults to 1000.
        wiggle (float, optional): wiggle factor when calculating the move direction. Defaults to 0.01.
        move_strength (float, optional): distance the node moves each step. Defaults to 0.01.
        number_of_nodes (int, optional): number of moving nodes. Defaults to 5.
        number_of_endpoints (int, optional): number of endpoints. Defaults to 2.
        seed (int, optional): generate the same random network each time with a seed. Defaults to 0.
        transmit_from_endpoints (bool, optional): choose whether endpoints can emit signals to nodes. Defaults to False.
    """

    from matplotlib import pyplot as plt
    from tqdm import trange

    nodes, connections = create_random_nodes(
        number_of_nodes, number_of_endpoints, seed, node_domain, endpoint_domain
    )

    for node in filter(lambda n: n.endpoint, nodes):
        plt.plot(node.pos.x, node.pos.y, "o", color=colors[node.id % len(colors)])
        plt.text(node.pos.x + 1, node.pos.y, f"endpoint {node.id}")

    for _ in trange(simulation_steps, desc="Simulating time steps"):
        for node in nodes:
            if draw_steps:
                plt.plot(
                    node.pos.x,
                    node.pos.y,
                    "o",
                    color=colors[node.id % len(colors)],
                    markersize=1,
                )
            node.send_routes(transmit_from_endpoints)

        directions = {
            node.id: find_move_direction(node, wiggle, move_strength)
            for node in nodes
            if not node.endpoint
        }
        for node in nodes:
            if node.endpoint:
                continue

            direction = directions[node.id]
            node.pos.x += direction.x
            node.pos.y += direction.y

        for connection in connections:
            connection.update_cost()

    max_strength = 1 / min(connection.cost for connection in connections)
    for node in filter(lambda n: not n.endpoint or transmit_from_endpoints, nodes):
        for source in set(map(lambda r: r.source, node.endpoint_routes.values())):
            if source == node.id:  # Do not plot the connection to itself.
                continue

            connection = node.connections[source]
            strength = 1 / connection.cost
            plt.plot(
                [n.pos.x for n in connection.nodes],
                [n.pos.y for n in connection.nodes],
                color="black",
                alpha=strength / max_strength,
            )

    if not draw_steps:
        for node in nodes:
            plt.plot(node.pos.x, node.pos.y, "o", color=colors[node.id % len(colors)])

    plt.show()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        prog="network-simulation",
        description="Simulate a network of nodes that move around to minimize the cost to the endpoints.",
    )

    argparser.add_argument(
        "-n",
        "--number-of-nodes",
        type=int,
        required=True,
        help="number of moving nodes",
    )
    argparser.add_argument(
        "-e",
        "--number-of-endpoints",
        type=int,
        required=True,
        help="number of endpoints",
    )
    argparser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="generate the same random network each time with a seed",
    )
    argparser.add_argument(
        "--simulation-steps", type=int, default=1000, help="number of steps to simulate"
    )
    argparser.add_argument(
        "--wiggle",
        type=float,
        default=0.01,
        help="wiggle factor when calculating the move direction",
    )
    argparser.add_argument(
        "-m",
        "--move-strength",
        type=float,
        default=0.01,
        help="distance the node moves each step",
    )
    argparser.add_argument(
        "-t",
        "--transmit-from-endpoints",
        action="store_true",
        help="choose whether endpoints can emit signals to nodes",
    )

    class DomainAction(argparse.Action):
        def __call__(
            self,
            parser: ArgumentParser,
            namespace: Namespace,
            values: list[int],
            option_string: str | None = None,
        ) -> None:
            if values[0] >= values[1]:
                raise argparse.ArgumentError(
                    self, "The first value needs to be smaller than the second value"
                )
            setattr(namespace, self.dest, values)

    argparser.add_argument(
        "--node-domain",
        nargs=2,
        type=float,
        action=DomainAction,
        default=[-20, 20],
        help="domain of the node positions",
    )
    argparser.add_argument(
        "--endpoint-domain",
        nargs=2,
        type=float,
        action=DomainAction,
        default=None,
        help="domain of the endpoint positions. this defaults to the node domain",
    )

    argparser.add_argument(
        "-d",
        "--draw-steps",
        action="store_true",
        help="draw each step of the simulation"
    )

    args = argparser.parse_args()

    # Run the simulation with argparse arguments
    try:
        simulate(
            args.simulation_steps,
            args.wiggle,
            args.move_strength,
            args.number_of_nodes,
            args.number_of_endpoints,
            args.seed,
            args.transmit_from_endpoints,
            args.node_domain,
            args.endpoint_domain,
            args.draw_steps
        )
    except ValueError as e:
        print(e)
        exit(1)
