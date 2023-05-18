from dataclasses import dataclass


@dataclass
class Node:
    """
    A node in the graph.
    """

    id: int
    pos: "Point"
    connections: dict[int, "Connection"]

    sink: "Route" = None
    drain: "Route" = None

    def process_routes(self, sink: "Route", drain: "Route") -> None:
        if sink is not None and (
            self.sink is None
            or sink.cost < self.sink.cost
            or (sink.source == self.sink.source)
        ):
            self.sink = sink
        if drain is not None and (
            self.drain is None
            or drain.cost < self.drain.cost
            or (drain.source == self.drain.source)
        ):
            self.drain = drain

    def send_routes(self) -> None:
        for connection in self.connections.values():
            connected_node = (
                connection.nodes[0]
                if connection.nodes[0].id != self.id
                else connection.nodes[1]
            )

            send_sink = (
                Route(self.id, self.sink.cost + connection.cost)
                if self.sink is not None
                else None
            )
            send_drain = (
                Route(self.id, self.drain.cost + connection.cost)
                if self.drain is not None
                else None
            )
            connected_node.process_routes(send_sink, send_drain)


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
    source: int
    cost: int


@dataclass
class Point:
    x: int
    y: int
