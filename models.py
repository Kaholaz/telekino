from dataclasses import dataclass

@dataclass
class Node:
    id: int
    pos: "Point"
    connections: dict[int, "Connection"]

    sink: "Route" = None
    drain: "Route" = None

@dataclass
class Connection:
    nodes: tuple[Node, Node]
    distance: int

    def __repr__(self) -> str:
        return f"Connection({self.nodes[0].id}, {self.nodes[1].id})"

@dataclass(frozen=True)
class Route:
    next_node: Node
    dist: float

@dataclass(frozen=True)
class Point:
    x: int
    y: int
