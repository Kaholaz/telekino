from dataclasses import dataclass, field


@dataclass
class Node:
    """
    A node in the graph.
    """

    id: int
    pos: "Point"
    connections: dict[int, "Connection"]

    endpoint: bool = False
    endpoint_routes: dict[int, "Route"] = field(default_factory=dict)

    def process_routes(self, endpoints: dict[int, "Route"]) -> None:
        """
        Process the routes from the connected nodes and update the endpoint_routes
        """

        for endpoint_id, route in endpoints.items():
            if (
                endpoint_id not in self.endpoint_routes
                or route.cost < self.endpoint_routes[endpoint_id].cost
            ):
                self.endpoint_routes[endpoint_id] = route

    def send_routes(self) -> None:
        """
        Send the routes to the connected nodes.
        """

        for connection in self.connections.values():
            connected_node = (
                connection.nodes[0]
                if connection.nodes[0].id != self.id
                else connection.nodes[1]
            )

            connected_node.process_routes(
                {
                    endpoint_id: Route(
                        self.id,
                        route.endpoint,
                        route.cost + connection.cost,
                    )
                    for endpoint_id, route in self.endpoint_routes.items()
                }
            )

    def make_endpoint(self) -> None:
        self.endpoint = True
        self.endpoint_routes = {self.id: Route(self.id, self.id, 0)}


@dataclass
class Connection:
    """
    A connection between two nodes.
    """

    nodes: tuple[Node, Node]
    cost: int

    def update_cost(self) -> float:
        """
        Call the calculate_cost method and update the cost attribute.
        """
        self.cost = self.calculate_cost()

    def calculate_cost(self) -> float:
        """
        Calculate the cost of the connection.
        """
        return (self.nodes[0].pos.x - self.nodes[1].pos.x) ** 2 + (
            self.nodes[0].pos.y - self.nodes[1].pos.y
        ) ** 2

    def __repr__(self) -> str:
        return f"Connection({self.nodes[0].id}, {self.nodes[1].id})"


@dataclass
class Route:
    """
    A route from the source to a node/endpoint and the cost of the route.
    """

    source: int
    endpoint: int
    cost: int


@dataclass
class Point:
    x: int
    y: int
