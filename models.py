from dataclasses import dataclass


@dataclass
class Node:
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
                Route(self.id, self.sink.cost, connection.cost)
                if self.sink is not None
                else None
            )
            send_drain = (
                Route(self.id, self.drain.cost, connection.cost)
                if self.drain is not None
                else None
            )
            connected_node.process_routes(send_sink, send_drain)


@dataclass
class Connection:
    nodes: tuple[Node, Node]
    distance: int

    @property
    def cost(self) -> int:
        return self.distance ** 2

    def __repr__(self) -> str:
        return f"Connection({self.nodes[0].id}, {self.nodes[1].id})"


@dataclass
class Route:
    source: int
    initial_cost: float
    added_cost: float = 0

    @property
    def cost(self) -> float:
        return self.initial_cost + self.added_cost


@dataclass(frozen=True)
class Point:
    x: int
    y: int
