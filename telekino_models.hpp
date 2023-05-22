#ifndef TELEKINO_MODELS
#define TELEKINO_MODELS

#include <unordered_map>
#include <utility>
#include <cmath>

class Point {
public:
    double x;
    double y;

    Point(double x, double y);
};

class Route {
public:
    int source;
    int endpoint;
    double cost;

    Route(int source, int endpoint, double cost);
};

class Node;  // Forward declaration for Connection class

class Connection {
public:
    std::pair<Node*, Node*> nodes;
    double cost;

    Connection(Node* node1, Node* node2, double cost);

    void update_cost();

    double calculate_cost();
};

class Node {
public:
    int id;
    Point pos;
    std::unordered_map<int, Connection*> connections;

    bool endpoint;
    std::unordered_map<int, Route*> endpoint_routes;

    Node(int id, const Point& pos);

    void process_routes(const std::unordered_map<int, Route*>& endpoints);

    void send_routes();

    void make_endpoint();

    Point find_move_direction(double wiggle = 0.01);

    double get_value();
};

#endif
