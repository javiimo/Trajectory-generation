#include <iostream>
#include <fstream>
#include <vector>
#include <string>

struct Point {
    double x, y;
};

void deserialize_points(const std::string& filename, 
                        std::vector<Point>& right_points, 
                        std::vector<Point>& left_points) {
    std::ifstream file(filename);
    std::string line;
    std::vector<Point>* current_vector = nullptr;

    while (std::getline(file, line)) {
        if (line == "RIGHT_POINTS") {
            current_vector = &right_points;
        } else if (line == "LEFT_POINTS") {
            current_vector = &left_points;
        } else if (current_vector) {
            Point p;
            if (sscanf(line.c_str(), "%lf %lf", &p.x, &p.y) == 2) {
                current_vector->push_back(p);
            }
        }
    }
}

/*
Example use:
std::vector<Point> right_points, left_points;
deserialize_points("points.txt", right_points, left_points);
*/