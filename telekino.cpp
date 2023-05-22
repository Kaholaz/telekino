#include <iostream>
#include <unordered_map>
#include <vector>
#include <cmath>
#include <random>
#include "telekino_models.hpp"

std::pair<std::vector<Node*>, std::vector<Connection*>> create_nodes(const std::vector<Point>& points, int endpoints) {
    std::vector<Node*> nodes;
    std::vector<Connection*> connections;

    for (int i = 0; i < points.size(); ++i) {
        Node* node = new Node(i, points[i]);
        nodes.push_back(node);
    }

    for (int i = 0; i < points.size(); ++i) {
        for (int j = i + 1; j < points.size(); ++j) {
            Connection* connection = new Connection(nodes[i], nodes[j], 0);
            connection->update_cost();
            connections.push_back(connection);

            nodes[i]->connections[j] = connection;
            nodes[j]->connections[i] = connection;
        }
    }

    for (int i = 0; i < endpoints; ++i) {
        nodes[i]->make_endpoint();
    }

    return {nodes, connections};
}

std::pair<std::vector<Node*>, std::vector<Connection*>> create_random_nodes(int number_of_nodes, int endpoints, std::pair<float, float> domain = {-20.0, 20.0}) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> dis(domain.first, domain.second);

    std::vector<Point> points;
    for (int i = 0; i < number_of_nodes; ++i) {
        float x = dis(gen);
        float y = dis(gen);
        points.push_back(Point(x, y));
    }

    auto [nodes, connections] = create_nodes(points, endpoints);
    return {nodes, connections};
}


std::vector<Node*> simulate(int number_of_nodes, int endpoints, int iterations, std::pair<float, float> domain = {-20.0, 20.0}) {
    std::cout << "Generating nodes" << std::endl;
    auto [nodes, connections] = create_random_nodes(number_of_nodes, endpoints, domain);

    std::cout << "Starting simulation" << std::endl;
    for (int i = 0; i < iterations; ++i) {
        std::cout << "Iteration " << i + 1  << " / " << iterations << std::endl;
        for (const auto& node : nodes) {
            node->send_routes();
        }

        for (const auto& node : nodes) {
            if (node->endpoint) continue;

            Point direction = node->find_move_direction();
            node->pos.x += direction.x;
            node->pos.y += direction.y;
        }

    }

    return nodes;
}

int main() {
    int number_of_nodes = 100;
    int number_of_endpoints = 10;
    int iterations = 1000;
    std::vector<Node*> nodes = simulate(number_of_nodes, number_of_endpoints, iterations);

    for (const auto& node : nodes) {
        std::cout << "Node " << node->id << " at (" << node->pos.x << ", " << node->pos.y << ")";
        std::cout << " is " << (node->endpoint ? "" : "not ") << "an endpoint" << std::endl;
    }
    return 0;
}