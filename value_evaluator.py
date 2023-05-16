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
            connected_node = connection.nodes[0] if connection.nodes[0].id != node.id else connection.nodes[1]
            inner(connected_node)
    inner(start)
    return nodes
    
@dataclass
class DijkstraNode:
    dist: int
    prev: int
    node: Node

def dijkstra(start: Node) -> dict[int, DijkstraNode]:
    heap = [DijkstraNode(0, -1, start)]

    result: dict[int, DijkstraNode] = {}
    while node := pop_heap(heap):
        if node.node.id in result:
            continue
        result[node.node.id] = node

        for connection in node.node.connections.values():
            if connection.distance > 6:
                continue
            connected_node = connection.nodes[0] if connection.nodes[0].id != node.node.id else connection.nodes[1]
            new_dist = node.dist + connection.distance - 3

            if connected_node.id not in result or new_dist < result[connected_node.id].dist:
                insert_heap(heap, DijkstraNode(new_dist, node.node.id, connected_node))

    return result

def update_distances(start: Node, end: Node) -> None:
    nodes = dfs_nodes(start)
    dijkstra_nodes = dijkstra(start)
    for node in nodes.values():
        dijkstra_node = dijkstra_nodes[node.id]
        if dijkstra_node.prev == -1: continue
        node.sink = Route(nodes[dijkstra_node.prev], dijkstra_node.dist)

    dijkstra_nodes = dijkstra(end)
    for node in nodes.values():
        dijkstra_node = dijkstra_nodes[node.id]
        if dijkstra_node.prev == -1: continue
        node.drain = Route(nodes[dijkstra_node.prev], dijkstra_node.dist)

def insert_heap(heap: list[DijkstraNode], node: DijkstraNode):
    position = len(heap)
    heap.append(node)

    while position > 0:
        parent_position = (position - 1) // 2
        parent = heap[parent_position]

        if node.dist < parent.dist:
            heap[parent_position], heap[position] = node, parent
            position = parent_position
        else:
            break

def heapify(heap: list[DijkstraNode]):
    if len(heap) == 0:
        return

    position = 0
    node = heap[position]

    while position < (len(heap) - 2) // 2:
        left_position = position * 2 + 1
        right_position = position * 2 + 2

        if right_position >= len(heap):
            candidate_position = left_position
        else:
            candidate_position = min(left_position, right_position, key=lambda x: heap[x].dist)

        candidate = heap[candidate_position]
        if candidate.dist < node.dist:
            heap[position], heap[candidate_position] = heap[candidate_position], heap[position]
            position = candidate_position
        else:
            break

def pop_heap(nodes: list[DijkstraNode]) -> Optional[DijkstraNode]:
    if len(nodes) == 0:
        return None

    node = nodes[0]
    nodes[0] = nodes[-1]
    nodes.pop()

    heapify(nodes)
    return node
