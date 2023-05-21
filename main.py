from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from typing import Any, Optional, Union

from models import Node, Connection, Point
import random
import argparse
from datetime import datetime

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

node_markersize = 0.8
endpoint_markersize = 3
endpoint_linewidth = 5


def create_random_nodes(
    number_of_nodes: int,
    endpoints: int,
    seed: Optional[int] = None,
    node_domain: tuple[float, float] = (-20, 20),
    endpoint_domain: Optional[tuple[float, float]] = None,
    max_connections: int = -1,
) -> tuple[list[Node], list[Connection]]:
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

    nodes, connections = create_nodes(points, endpoints, max_connections)

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
    points: list[Point], endpoints: int, max_connections: int = -1
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

    for node in nodes[endpoints:]:
        node.top_connections = sorted(
            list(node.connections.values()), key=lambda c: c.cost
        )[:max_connections]

    return nodes, connections


def get_value(node: Node) -> float:
    """
    Compute the nodes worth based on the cost from all routes to the connected endpoints.
    """

    connected_nodes = {route.source for route in node.endpoint_routes.values()}
    return -sum(
        node.connections[connected_node].calculate_cost()
        for connected_node in connected_nodes
    ) * len(connected_nodes)


def find_move_direction(
    node: Node, wiggle: float, move_strength: float, max_speed: float
) -> Point:
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
    speed_x = dx / wiggle * move_strength
    speed_y = dy / wiggle * move_strength

    # Limit the speed of the node.
    speed_x = min(max_speed, max(-max_speed, speed_x))
    speed_y = min(max_speed, max(-max_speed, speed_y))

    return Point(speed_x, speed_y)


def simulate(
    simulation_steps: int = 1000,
    wiggle: float = 0.01,
    move_strength: float = 0.01,
    number_of_nodes: int = 5,
    number_of_endpoints: int = 2,
    seed: Optional[int] = None,
    transmit_from_endpoints: bool = False,
    node_domain: tuple[float, float] = (-20, 20),
    endpoint_domain: Optional[tuple[float, float]] = None,
    draw_steps: bool = True,
    export: bool = False,
    max_speed: float = 5,
    max_connections: int = -1,
) -> None:
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

    from matplotlib import pyplot as plt  # type: ignore
    from tqdm import trange

    nodes, connections = create_random_nodes(
        number_of_nodes,
        number_of_endpoints,
        seed,
        node_domain,
        endpoint_domain,
        max_connections,
    )

    for _ in trange(simulation_steps, desc="Simulating time steps"):
        for node in nodes:
            if draw_steps:
                plt.plot(
                    node.pos.x,
                    node.pos.y,
                    "o",
                    color=colors[node.id % len(colors)],
                    markersize=node_markersize,
                )
            node.send_routes(transmit_from_endpoints)

        directions = {
            node.id: find_move_direction(node, wiggle, move_strength, max_speed)
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

    # Plot the connections
    min_cost = min(connection.cost for connection in connections)
    max_strength = 1 / max(min_cost, 0.001)
    for node in filter(lambda n: not n.endpoint or transmit_from_endpoints, nodes):
        for source in set(map(lambda r: r.source, node.endpoint_routes.values())):
            if source == node.id:  # Do not plot the connection to itself.
                continue

            connection = node.connections[source]
            if connection.cost <= 0:
                continue
            strength = 1 / connection.cost
            plt.plot(
                [n.pos.x for n in connection.nodes],
                [n.pos.y for n in connection.nodes],
                color="black",
                alpha=min(1, (strength / max_strength) ** 0.3),
            )

    if not draw_steps:
        for node in filter(lambda n: not n.endpoint, nodes):
            plt.plot(
                node.pos.x,
                node.pos.y,
                "o",
                color=colors[node.id % len(colors)],
                markersize=node_markersize,
            )

    # Plot endpoints
    for node in filter(lambda n: n.endpoint, nodes):
        plt.plot(
            node.pos.x,
            node.pos.y,
            marker="P",
            color=colors[node.id % len(colors)],
            markersize=endpoint_markersize,
            linewidth=endpoint_linewidth,
        )
        plt.text(node.pos.x + 1, node.pos.y, f"endpoint {node.id}")

    if export:
        time = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        # file name is time + all args separated by underscores
        filename = f"{time}_{simulation_steps=}_{wiggle=}_{move_strength=}_{number_of_nodes=}_{number_of_endpoints=}_{seed=}_{transmit_from_endpoints=}_{node_domain=}_{endpoint_domain=}.png"
        plt.savefig(filename, bbox_inches="tight", dpi=2000)
    else:
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
        help="number of endpoints to generate",
    )
    argparser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="create a seed to generate the same random network each time",
    )
    argparser.add_argument(
        "-s",
        "--simulation-steps",
        type=int,
        default=1000,
        help="number of steps to simulate",
    )
    argparser.add_argument(
        "-w",
        "--wiggle",
        type=float,
        default=0.01,
        help="distance (dx and dy) the node travels when calculating the move direction",
    )
    argparser.add_argument(
        "-m",
        "--move-strength",
        type=float,
        default=0.01,
        help="distance the node moves each step",
    )
    argparser.add_argument(
        "--transmit-from-endpoints",
        action="store_true",
        help="choose whether endpoints can emit signals back to nodes",
    )

    class DomainAction(argparse.Action):
        def __call__(
            self,
            parser: ArgumentParser,
            namespace: Namespace,
            values: Union[str, Sequence[Any], None],
            option_string: Optional[str] = None,
        ) -> None:
            if values is None or type(values) == str or len(values) != 2:
                raise argparse.ArgumentError(
                    self, "The domain needs to be a sequence of two values"
                )
            if values[0] >= values[1]:
                raise argparse.ArgumentError(
                    self, "The first value needs to be smaller than the second value"
                )
            setattr(namespace, self.dest, values)

    argparser.add_argument(
        "-nd",
        "--node-domain",
        nargs=2,
        type=float,
        action=DomainAction,
        default=[-20, 20],
        help="domain of where the node positions are generated",
    )
    argparser.add_argument(
        "-ed",
        "--endpoint-domain",
        nargs=2,
        type=float,
        action=DomainAction,
        default=None,
        help="domain of where the endpoint positions are generated. this defaults to the node domain",
    )

    argparser.add_argument(
        "-d",
        "--draw-steps",
        action="store_true",
        help="draw each step of the simulation on the graph",
    )

    argparser.add_argument(
        "-x",
        "--export",
        action="store_true",
        help="export the simulation as a png",
    )

    def positive_float(value: str) -> float:
        try:
            fvalue = float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"{value} is an invalid positive float value"
            )

        if fvalue <= 0:
            raise argparse.ArgumentTypeError(
                f"{value} is an invalid positive float value"
            )
        return fvalue

    argparser.add_argument(
        "--max-speed",
        type=positive_float,
        default=5,
        help="maximum speed of the nodes",
    )

    def positive_int(value: str) -> int:
        try:
            ivalue = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"{value} is an invalid positive int value"
            )

        if ivalue <= 0:
            raise argparse.ArgumentTypeError(
                f"{value} is an invalid positive int value"
            )
        return ivalue

    argparser.add_argument(
        "-c",
        "--max-connections",
        type=positive_int,
        default=-1,
        help="maximum number of connections per node. Improves simulation speed on large networks"
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
            args.draw_steps,
            args.export,
            args.max_speed,
            args.max_connections,
        )
    except ValueError as e:
        print(e)
        exit(1)
