#include <iostream>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <cmath>
#include <random>
#include <mutex>
#include "telekino_models.hpp"

Point::Point(double x, double y) : x(x), y(y) {}

Route::Route(int source, int endpoint, double cost) : source(source), endpoint(endpoint), cost(cost) {}

Connection::Connection(Node* node1, Node* node2, double cost) : cost(cost) {
    nodes.first = node1;
    nodes.second = node2;
}

void Connection::update_cost() {
    this->cost = calculate_cost();
}

double Connection::calculate_cost() {
    return pow(nodes.first->pos.x - nodes.second->pos.x, 2) +
           pow(nodes.first->pos.y - nodes.second->pos.y, 2);
};

Node::Node(int id, const Point& pos) : id(id), pos(pos) {}

void Node::process_routes(const std::unordered_map<int, Route*>& endpoints) {
    std::lock_guard<std::mutex> lock(endpoint_routes_mutex);
    for (const auto& endpoint : endpoints) {
        int endpoint_id = endpoint.first;
        const auto& route = endpoint.second;
        if (endpoint_routes.find(endpoint_id) == endpoint_routes.end() ||
            route->cost < endpoint_routes[endpoint_id]->cost) {
            endpoint_routes[endpoint_id] = route;
        }
    }
}

void Node::send_routes() {
    for (const auto& connection : connections) {
        Node* connected_node = (connection.second->nodes.first != this) ?
                                connection.second->nodes.first :
                                connection.second->nodes.second;

        std::unordered_map<int, Route*> new_endpoint_routes;
        for (const auto& route : endpoint_routes) {
            int endpoint_id = route.first;
            const auto& route_info = route.second;
            new_endpoint_routes[endpoint_id] = new Route(
                id,
                route_info->endpoint,
                route_info->cost + connection.second->cost
            );
        }

        connected_node->process_routes(new_endpoint_routes);
    }
}

void Node::make_endpoint() {
    endpoint = true;
    endpoint_routes[id] = new Route(id, id, 0);
}

Point Node::find_move_direction(double wiggle) {
    if (endpoint_routes.size() < 2) {
        std::cout << "Node " << id << " has less than 2 routes" << std::endl;
        return Point(0, 0);
    }

    double current_value = get_value();

    pos.x += wiggle;
    double new_value = get_value();
    double dx = new_value - current_value;

    pos.x -= wiggle;
    pos.y += wiggle;
    new_value = get_value();
    double dy = new_value - current_value;

    pos.y -= wiggle;

    return Point(dx, dy);
}

double Node::get_value() {
    double value = 0.0;

    std::vector<int> source_ids = {};
    for (const auto& route : endpoint_routes) {
        int source = route.second->source;

        // Discard non-unique source ids
        if (std::find(source_ids.begin(), source_ids.end(), source) != source_ids.end()) {
            continue;
        }

        // Subtract the cost of the connection to the source of the route from the value
        source_ids.push_back(source);
        const auto& connection = connections[source];
        value -= connection->calculate_cost();
    }

    return value;
}
