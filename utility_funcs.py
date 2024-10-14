import math
import random
import os
import datetime

#! LINE FUNCTIONS
def compute_slope(p1, p2):
    """
    Computes the slope of the line defined by two points.

    Args:
        p1 (list or tuple): The first point [x1, y1].
        p2 (list or tuple): The second point [x2, y2].

    Returns:
        float: The slope of the line. Returns float('inf') if the line is vertical.
    """
    if abs(p1[0] - p2[0]) < 1e-14:  # Check for vertical line with a small threshold
        return float('inf')
    return (p2[1] - p1[1]) / (p2[0] - p1[0])


def get_line_function(slope, point):
    """
    Returns a function that represents a line given its slope and a point.

    Args:
        slope (float): The slope of the line.
        point (list or tuple): A point on the line [x1, y1].

    Returns:
        function: A function that takes an x-value and returns the corresponding y-value on the line.
        float: Returns the x-value if the line is vertical.
    """
    x1, y1 = point

    if slope == float('inf'):
        print("Vertical line given, returning the x value")
        return x1
    
    def line_function(x):
        return slope * (x - x1) + y1
    return line_function


def find_intersection(slope1, point1, slope2, point2):
    """
    Finds the intersection point of two lines defined by their slopes and a point on each line.

    Args:
        slope1 (float): The slope of the first line.
        point1 (list or tuple): A point on the first line [x1, y1].
        slope2 (float): The slope of the second line.
        point2 (list or tuple): A point on the second line [x2, y2].

    Returns:
        list: The intersection point [x, y] or None if the lines are parallel.
    """
    # Unpack the points
    x1, y1 = point1
    x2, y2 = point2

    # Handle cases with infinite or -0.0 slopes
    if slope1 == float('inf') or slope1 == -0.0:
        x = x1
        y = slope2 * (x - x2) + y2
    elif slope2 == float('inf') or slope2 == -0.0:
        x = x2
        y = slope1 * (x - x1) + y1
    # Check if the slopes are the same (parallel lines)
    elif abs(slope1 - slope2) < 1e-14:
        return None  # No intersection (or infinite intersections if they are the same line)
    else:
        # Calculate the intersection x-coordinate
        x = (y2 - y1 + slope1 * x1 - slope2 * x2) / (slope1 - slope2)

        # Calculate the intersection y-coordinate using the equation of the first line
        y = slope1 * x + (y1 - slope1 * x1)

    return [x, y]





#! VECTOR FUNCTIONS
def compute_vector(p_i, p_f):
    """
    Computes the vector from an initial point to a final point.

    Args:
        p_i (list or tuple): The initial point [x_i, y_i].
        p_f (list or tuple): The final point [x_f, y_f].

    Returns:
        list: The vector from p_i to p_f [x_f - x_i, y_f - y_i].
    """
    return [p_f[0]-p_i[0], p_f[1]-p_i[1]]


def normalize_vector(vector):
    """Normalizes a vector using the Euclidean norm.

    Args:
        vector (list): The vector to normalize.

    Returns:
        list: The normalized vector, or None if the vector has zero length.
    """
    norm = math.sqrt(vector[0]**2 + vector[1]**2)
    if norm == 0:
        return None
    return [vector[0] / norm, vector[1] / norm]


def scalar_mul(vect, scalar):
    return [vect[0]*scalar, vect[1]*scalar]


def add(vect1, vect2):
    return [vect1[0]+vect2[0], vect1[1]+vect2[1]]


def get_perpendicular_vector(vector):
    """Given a vector, returns the perpendicular vector."""
    return [-vector[1], vector[0]]


def rotate_180(vector):
    """
    Rotates a vector 180 degrees.

    Args:
        vector (list or tuple): The vector to rotate [x, y].

    Returns:
        list: The rotated vector [-x, -y].
    """
    return [-vector[0], -vector[1]]


def rotate_vector(vector, degrees):
    """
    Rotates a 2D vector by a specified angle in degrees counterclockwise.

    Args:
        vector (list or tuple): The vector to rotate [x, y].
        degrees (float): The angle of rotation in degrees.

    Returns:
        list: The rotated vector [x', y'].
    """
    # Convert degrees to radians
    radians = math.radians(degrees)

    # Rotation matrix
    cos_theta = math.cos(radians)
    sin_theta = math.sin(radians)

    # Apply rotation matrix
    x_prime = vector[0] * cos_theta - vector[1] * sin_theta
    y_prime = vector[0] * sin_theta + vector[1] * cos_theta

    return [x_prime, y_prime]



def is_clockwise(vector1, vector2):
    """
    Determine if the rotation from vector1 to vector2 is clockwise using the sign of the cross product

    Parameters:
    vector1 (list or tuple): The first vector [x, y].
    vector2 (list or tuple): The second vector [x, y].

    Returns:
    bool: True if the rotation is clockwise, False if counterclockwise.
    """
    x1, y1 = vector1
    x2, y2 = vector2
    
    # Calculate the cross product in 2D
    cross_product = x1 * y2 - y1 * x2
    if abs(cross_product)/euclidean_norm(vector1,[0,0])*euclidean_norm(vector2,[0,0]) <= 0.2:
        return None #This is in case the points are aligned, don't rotate
    
    # If the cross product is negative, the rotation is clockwise
    # If the cross product is positive, the rotation is counterclockwise
    return cross_product < 0




#!POINT FUNCTIONS
def compute_midpoint(p1, p2):
    """
    Computes the midpoint of the line segment defined by two points.

    Args:
        p1 (list or tuple): The first point [x1, y1].
        p2 (list or tuple): The second point [x2, y2].

    Returns:
        list: The midpoint of the line segment [x_mid, y_mid].
    """
    return [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]


def euclidean_norm(p1, p2):
    """
    Computes the Euclidean distance between two points.

    Args:
        p1 (list or tuple): The first point [x1, y1].
        p2 (list or tuple): The second point [x2, y2].

    Returns:
        float: The Euclidean distance between the two points.
    """
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5




#! OTHER

def random_partition(start, end, min_distance, max_distance):
    """Generates a list of points between a start and end value, with random spacing.

    Args:
        start (float): The starting value.
        end (float): The ending value.
        min_distance (float): The minimum distance between consecutive points.
        max_distance (float): The maximum distance between consecutive points.

    Returns:
        list[float]: A list of points, including the start and end values.
    """
    if start >= end:
        return []

    points = [start]
    while points[-1] < end:
        next_point = points[-1] + random.uniform(min_distance, max_distance)
        if next_point > end:
            break
        points.append(next_point)

    if points[-1] != end:
        points.append(end)

    return points


def get_curve_points(a, b, radius, angle_degrees):
    
    angle_radians = math.radians(angle_degrees)
    x = a + radius * math.cos(angle_radians)
    y = b + radius * math.sin(angle_radians)
    
    return [x, y]


def arc_to_angle(arc_length, radius):
  """Calculates the angle increment in degrees for a given arc length and radius.

  Args:
    arc_length: The length of the arc in meters.
    radius: The radius of the circle in meters.

  Returns:
    The angle increment in degrees.
  """
  return math.degrees(arc_length / radius)


def angle_to_arc(angle_degrees, radius):
  """Calculates the arc length in meters for a given angle and radius.

  Args:
    angle_degrees: The angle in degrees.
    radius: The radius of the circle in meters.

  Returns:
    The arc length in meters.
  """
  angle_radians = math.radians(angle_degrees)
  return radius * angle_radians


def first_different_index(list1, list2):
    """
    Compares two lists and returns the index of the first element that differs between them.

    Args:
        list1: The first list.
        list2: The second list.

    Returns:
        int: The index of the first difference, or -1 if the lists are identical 
        or one is a prefix of the other.
    """
    min_len = min(len(list1), len(list2))
    for i in range(min_len):
        if list1[i] != list2[i]:
            return i
    return min_len   # Lists are identical up to the length of the shorter list


#! Serializing and deserializing points
def deserialize_points(file_path="map.dat"):
    """
    Deserializes points from a file into two lists: right_points and left_points.

    The file should have the following format:

    RIGHT_POINTS
    x1 y1
    x2 y2
    ...
    LEFT_POINTS
    x1 y1
    x2 y2
    ...

    Args:
        file_path (str): The path to the file containing the points. Defaults to "map.dat".

    Returns:
        tuple: A tuple containing two lists: right_points and left_points.
    """
    right_points = []
    left_points = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

            current_list = None
            for line in lines:
                line = line.strip()
                if line == "RIGHT_POINTS":
                    current_list = right_points
                elif line == "LEFT_POINTS":
                    current_list = left_points
                elif line and current_list is not None:
                    # Split the line into coordinates and convert to float
                    point = list(map(float, line.split()))
                    current_list.append(point)

    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None, None  # Return None for both lists in case of an error

    return right_points, left_points


def serialize_points(right_points, left_points, filename = "points", logs_folder="logs"):
    """
    Serializes two lists of points, right_points and left_points, into a file within the 'logs' folder.
    The file name is a timestamp.

    The file will have the following format:

    RIGHT_POINTS
    x1 y1
    x2 y2
    ...
    LEFT_POINTS
    x1 y1
    x2 y2
    ...

    Args:
        right_points (list): A list of right points, where each point is a list or tuple [x, y].
        left_points (list): A list of left points, where each point is a list or tuple [x, y].
        logs_folder (str): The path to the logs folder. Defaults to "logs".

    Returns:
        bool: True if the points were successfully serialized, False otherwise.
    """
    try:
        # Create the logs folder if it doesn't exist
        os.makedirs(logs_folder, exist_ok=True)

        # Generate timestamped filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(logs_folder, f"{filename}_{timestamp}.log")

        with open(file_path, 'w') as file:
            # Write right points
            file.write("RIGHT_POINTS\n")
            for point in right_points:
                file.write(f"{point[0]} {point[1]}\n")

            # Write left points
            file.write("LEFT_POINTS\n")
            for point in left_points:
                file.write(f"{point[0]} {point[1]}\n")
        return True

    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")
        return False


def serialize_midpoints(mid_points, filename="midpoints", logs_folder="logs"):
    """
    Serializes a list of midpoints into a file within the 'logs' folder.
    The file name is a timestamp.

    The file will have the following format:

    MID_POINTS
    x1 y1
    x2 y2
    ...

    Args:
        mid_points (list): A list of midpoints, where each point is a list or tuple [x, y].
        logs_folder (str): The path to the logs folder. Defaults to "logs".

    Returns:
        bool: True if the points were successfully serialized, False otherwise.
    """
    try:
        # Create the logs folder if it doesn't exist
        os.makedirs(logs_folder, exist_ok=True)

        # Generate timestamped filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(logs_folder, f"{filename}_{timestamp}.log")

        with open(file_path, 'w') as file:
            # Write midpoints
            file.write("MID_POINTS\n")
            for point in mid_points:
                if point: # Check if the point is not None or empty
                    file.write(f"{point[0]} {point[1]}\n")

        return True

    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")
        return False


def deserialize_midpoints(file_path):
    """
    Deserializes a list of midpoints from a file.

    Args:
        file_path (str): The path to the file containing the midpoints.

    Returns:
        list: A list of midpoints, where each point is a list [x, y], or None if an error occurs.
    """
    try:
        mid_points = []
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if lines and lines[0].strip() == "MID_POINTS":
                for line in lines[1:]:
                    try:
                        x, y = map(float, line.split())
                        mid_points.append([x, y])
                    except ValueError:
                        print(f"Skipping invalid line: {line.strip()}")
                        return None # Or handle the error differently, e.g., continue
            else:
                print("Invalid file format. Expected 'MID_POINTS' at the beginning.")
                return None
        return mid_points

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None
