from dataclasses import dataclass, field


@dataclass
class Node:
    """
    A node in the graph.
    """

    id: int
    pos: "Point"
    connections: dict[int, "Connection"]
    top_connections: list["Connection"] = field(default_factory=list)

    endpoint: bool = False
    endpoint_routes: dict[int, "Route"] = field(default_factory=dict)

    def process_routes(
        self, endpoints: dict[int, "Route"], transmit_from_endpoint: bool
    ) -> None:
        """
        Process the routes from the connected nodes and update the endpoint_routes
        """

        if self.endpoint and not transmit_from_endpoint:
            return

        for endpoint_id, route in endpoints.items():
            if (
                endpoint_id not in self.endpoint_routes
                or route.cost < self.endpoint_routes[endpoint_id].cost
            ):
                self.endpoint_routes[endpoint_id] = route

    def send_routes(self, transmit_from_endpoint: bool) -> None:
        """
        Send the routes to the connected nodes.
        """
        for connection in self.top_connections:
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
                },
                transmit_from_endpoint,
            )

    def make_endpoint(self) -> None:
        self.endpoint = True
        self.endpoint_routes = {self.id: Route(self.id, self.id, 0)}
        self.top_connections = list(self.connections.values())


@dataclass
class Connection:
    """
    A connection between two nodes.
    """

    __slots__ = ["nodes", "cost"]

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

    __slots__ = ["source", "endpoint", "cost"]
    source: int
    endpoint: int
    cost: int


@dataclass
class Point:
    __slots__ = ["x", "y"]
    x: int
    y: int
