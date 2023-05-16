from typing import Optional
from models import Node, Route
from dataclasses import dataclass


def dfs_nodes(start: Node) -> dict[int, Node]:
    nodes: dict[int, Node] = {}

    def inner(node):
        if node.id in nodes:
            return

        nodes[node.id] = node
        for connection in node.connections.values():
            connected_node = (
                connection.nodes[0]
                if connection.nodes[0].id != node.id
                else connection.nodes[1]
            )
            inner(connected_node)

    inner(start)
    return nodes
