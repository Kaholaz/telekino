#include <iostream>
#include <unordered_map>
#include <vector>
#include <cmath>
#include <random>
#include <thread>
#include <chrono>
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


std::vector<Node*> simulate(int number_of_nodes, int endpoints, int durationInSeconds, std::pair<float, float> domain = {-20.0, 20.0}) {
    std::cout << "Generating nodes" << std::endl;
    auto [nodes, connections] = create_random_nodes(number_of_nodes, endpoints, domain);

    std::cout << "Starting simulation" << std::endl;

    // Flag to signal worker threads to stop
    bool stopSimulation = false;

    std::vector<std::thread> threads;

    auto nodeThreadFunction = [&](Node* node) {
        auto startTime = std::chrono::steady_clock::now();
        while (!stopSimulation) {
            node->send_routes();

            if (!node->endpoint) {
                Point direction = node->find_move_direction();
                node->pos.x += direction.x;
                node->pos.y += direction.y;
            }
            std::this_thread::yield();
        }

        auto endTime = std::chrono::steady_clock::now();
        auto elapsedSeconds = std::chrono::duration_cast<std::chrono::seconds>(endTime - startTime).count();
        std::cout << "Node " << node->id << " finished after " << elapsedSeconds << " seconds." << std::endl;
    };

    for (const auto& node : nodes) {
        // Spawn a thread for each node and pass the node as an argument
        threads.emplace_back(nodeThreadFunction, node);
    }


    auto startTime = std::chrono::steady_clock::now();
    int64_t elapsedSeconds = 0;
    do {
        auto now = std::chrono::steady_clock::now();
        elapsedSeconds = std::chrono::duration_cast<std::chrono::seconds>(now - startTime).count();
        std::cout << "Elapsed time: " << elapsedSeconds << " seconds" << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    } while (elapsedSeconds < durationInSeconds);

    stopSimulation = true;

    for (auto& thread : threads) {
        thread.join();
    }

    return nodes;
}

int main() {
    int number_of_nodes = 50;
    int number_of_endpoints = 5;
    int durationsInSeconds = 120;
    std::vector<Node*> nodes = simulate(number_of_nodes, number_of_endpoints, durationsInSeconds);

    for (const auto& node : nodes) {
        std::cout << node->pos.x << "," << node->pos.y << std::endl; 
    }
    return 0;
}
