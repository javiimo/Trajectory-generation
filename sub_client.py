import sys
import zmq
import os
import matplotlib.pyplot as plt
import random
import multiprocessing



# UTILITY FUNCTIONS FOR THE TRAJECTORY COMPUTATION -----------------------------------------------
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


def rotate_180(vector):
    """
    Rotates a vector 180 degrees.

    Args:
        vector (list or tuple): The vector to rotate [x, y].

    Returns:
        list: The rotated vector [-x, -y].
    """
    return [-vector[0], -vector[1]]


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


def order_point_list(list):
    """Orders a list of points based on proximity to the last ordered point. It takes the first point in the list as a starting point.

    Args:
        list: A list of points.

    Returns:
        A new list with the points ordered based on proximity.
    """
    # Assume the first point is still the first point
    ordered_list = [list[0]] #Assume the first point is ordered correctly
    remaining_points = list[1:]
    while remaining_points:
        closest_point = min(remaining_points, key=lambda point: euclidean_norm(ordered_list[-1], point))
        ordered_list.append(closest_point)
        remaining_points.remove(closest_point)

    return ordered_list


def order_point_list_semiplane(list, line_func = None, semiplane = None):
    """Orders a list of points based on proximity to the last ordered point,
    considering a dividing line and a desired semiplane to choose the second point in the list.

    Args:
        list: A list of points.
        line_func: A function that defines the dividing line. Can be a callable
                   or a constant for vertical lines.
        semiplane: +1 to select points above the line, -1 for points below.

    Returns:
        A new list with the points ordered based on proximity and semiplane.
    """
    # Assume the first point is still the first point
    ordered_list = [list[0]] #Assume the first point is ordered correctly
    remaining_points = list[1:]
    if semiplane is None:
        while remaining_points:
            closest_point = min(remaining_points, key=lambda point: euclidean_norm(ordered_list[-1], point))
            ordered_list.append(closest_point)
            remaining_points.remove(closest_point)

    elif callable(line_func):
        remaining_points_copy = remaining_points.copy()
        while remaining_points_copy:
            closest_point = min(remaining_points_copy, key=lambda point: euclidean_norm(ordered_list[-1], point))
            if line_func(closest_point[0]) * semiplane < closest_point[1] * semiplane:
                ordered_list.append(closest_point) 
                remaining_points.remove(closest_point)
            remaining_points_copy.remove(closest_point)
        
        if len(ordered_list)<2:
            print("Failed to order the points in the given direction. Try changing the chosen semiplane")
        
        while remaining_points:
            closest_point = min(remaining_points, key=lambda point: euclidean_norm(ordered_list[-1], point))
            ordered_list.append(closest_point)
            remaining_points.remove(closest_point)
    
    else:
        # Case of vertical line
        remaining_points_copy = remaining_points.copy()
        while remaining_points_copy and len(ordered_list)<2:
            closest_point = min(remaining_points_copy, key=lambda point: euclidean_norm(ordered_list[-1], point))
            if line_func * semiplane < closest_point[0] * semiplane:
                ordered_list.append(closest_point) 
                remaining_points.remove(closest_point)
            remaining_points_copy.remove(closest_point)

        if len(ordered_list)<2:
            print("Failed to order the points in the given direction. Try changing the chosen semiplane")
        
        while remaining_points:
            closest_point = min(remaining_points, key=lambda point: euclidean_norm(ordered_list[-1], point))
            ordered_list.append(closest_point)
            remaining_points.remove(closest_point)
    
    return ordered_list

def order_both_lists_of_cones(rpoints, lpoints, semiplane = None):
    """Orders two lists of points (presumably right and left cones) based on 
    proximity and a dividing line defined by the first points of each list.

    Args:
        rpoints: The list of points for the right cones.
        lpoints: The list of points for the left cones.
        semiplane: +1 to select points above the line (or to the right if the line is vertical), -1 for points below (or to the left).

    Returns:
        A list containing the two ordered lists of points.
    """
    # side can be +1 (above the line) or -1 (below the line)
    p1 = rpoints[0]
    p2 = lpoints[0]
    slope = compute_slope(p1, p2)

    line = get_line_function(slope, p1)

    rpoints = order_point_list_semiplane(rpoints, line, semiplane)
    lpoints = order_point_list_semiplane(lpoints, line, semiplane)

    return [rpoints, lpoints]


def compute_trajectory(right_points, left_points, semiplane = None):
    """Computes the trajectory of the car by iteratively finding the midpoint between the next right and left cones.

    This function calculates the car's trajectory based on the positions of right and left cones. It iteratively identifies the next right or left cones and computes the midpoint between them. This midpoint serves as the next point in the trajectory. The algorithm considers the distances between cones to determine which cone to select next, ensuring a smooth and accurate trajectory.

    The function also handles cases where one side (right or left) has more cones than the other. In such scenarios, it continues to follow the remaining cones until all cones have been considered.

    Args:
        right_points (list): A list of coordinates representing the right cones.
        left_points (list): A list of coordinates representing the left cones.
        semiplane (int, optional): An optional parameter indicating the desired side of the track (+1 for above or right, -1 for below or left). Defaults to None.

    Returns:
        list: A list of coordinates representing the computed trajectory.

    Algorithm:
        1. Order the right and left cones based on proximity and a dividing line defined by the first points of each list.
        2. Add the midpoint of the first right and left cones as the starting point of the trajectory.
        3. Iterate until all cones on either side have been considered:
            a. Calculate the distances between the current midpoint and the next right and left cones.
            b. Select the side (right or left) with the shorter distance.
            c. Compute the slope between the selected new last cone and the previous cone on the same side.
            d. Calculate the perpendicular slope to the computed slope.
            e. Find the intersection point between the line defined by the computed slope and the last midpoint, and the line defined by the perpendicular slope and the new last cone.
            f. Add the intersection point as the next point in the trajectory.
            g. Make sure the cone is exactly 1.5m away from the new last cone (This hyperparameter comes from the minimum width of the track being 3m)
            h. Use the clockwise and counterclockwise computation to make sure right cones are always to the right and left cones are always to the left. If not, rotate 180º respect to the new last cone.
            i. Make sure the mid point list is ordered, no going forward and backward suddenly
            j. To prevent erratic trajectories on wider track sections, we average trajectory points that are less than 2 meters apart.
                -This helps avoid excessively close trajectory points.
                -However, this approach might be problematic if numerous cones are clustered together.
                -A potential alternative could involve skipping the averaging step for 2 or 3 consecutive iterations. Or using the info of the distance between cones of the same side.
        4. Return the list of trajectory points.

        Note:
            - This algorithm can work with just 2 cones from only one side and uses the information of all the cones registered from both sides to improve the predicted trajectory if more cones are given. But it strongly relies on distinguishing perfectly between right and left cones, if it missunderstands that, it will almost for sure get out of the track.
            
            - There are 2 hyperparameters that depend on the expected separation of the cones and the size of the vehicle, which are the thresholds of stepts g and j
    """
    # Assert the points are correctly ordered
    rpoints, lpoints = order_both_lists_of_cones(right_points, left_points, semiplane)

    # Add first trajectory point
    start_point = compute_midpoint(rpoints[0], lpoints[0])
    mid_points = [start_point]

    # Auxiliary variables
    last_ri = 0
    last_li = 0
    # Main loop
    while last_ri < len(rpoints) - 1 or last_li < len(lpoints) - 1:
        if last_ri < len(rpoints) - 1 and last_li < len(lpoints) - 1:
            distr = euclidean_norm(rpoints[last_ri], rpoints[last_ri+1]) + euclidean_norm(lpoints[last_li], rpoints[last_ri+1])
            distl = euclidean_norm(lpoints[last_li], lpoints[last_li+1]) + euclidean_norm(rpoints[last_ri], lpoints[last_li+1])
        #Cases in which we run out of points in one side but still have points remaining in the other side:
        elif last_ri < len(rpoints) - 1:
            distr = 0  # Force right side movement
            distl = float('inf')
        else:
            distr = float('inf')
            distl = 0  # Force left side movement

        if distr <= distl:
            right = True
            last_ri += 1
            last_cone = rpoints[last_ri]
            other_last_cone = lpoints[last_li]
            anchor_slope = rpoints[last_ri-1]
            slope = compute_slope(anchor_slope, last_cone)

        else:
            right = False
            last_li += 1
            last_cone = lpoints[last_li]
            other_last_cone = rpoints[last_ri]
            anchor_slope = lpoints[last_li-1]
            slope = compute_slope(anchor_slope, last_cone)
        
    
        perp_slope = float('inf') if slope == 0 else -1 / slope
        new_point = find_intersection(slope, mid_points[-1], perp_slope, last_cone)

        #Set the distance to the last cone exactly 1.5
        if euclidean_norm(new_point, last_cone) != 1.5:
            vector = compute_vector(last_cone, new_point)
            norm = euclidean_norm(vector, [0,0])
            vector = [1.5 * vector[0]/norm, 1.5 * vector[1]/norm]
            new_point = [last_cone[0] + vector[0], last_cone[1] + vector[1]]
            
        # Rotate 180 respect to the last cone if the new point is to the left of the left cone or to the right of the right cone:
        cond = is_clockwise(compute_vector(other_last_cone, last_cone), compute_vector(other_last_cone, new_point))
        if cond is not None: 
            cond = cond if right else not cond #Distinguish between last cone being left cone or right cone
            if cond == True:
                vector = compute_vector(last_cone, new_point)
                vector = rotate_180(vector)
                new_point = [last_cone[0] + vector[0], last_cone[1] + vector[1]]

        mid_points.append(new_point)

        # Order last 3 trajectory points (not needed in most cases, just a safety check)
        if len(mid_points)>=3:
            mid_points[-3:] = order_point_list(mid_points[-3:])

        # In case 2 trajectory points are too close, remove them and take only the average point
        if euclidean_norm(mid_points[-1], mid_points[-2]) < 2 :
            mid_point = [(mid_points[-1][0] + mid_points[-2][0])/2, (mid_points[-1][1] + mid_points[-2][1])/2]
            mid_points[-2:] = [mid_point]

        #Plotting the step:
    return mid_points



def receiver(right_points, left_points, port = "5556"):
    # Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    print("Starting the receiver...")
    socket.connect ("tcp://localhost:%s" % port)

    # Subscribe to the right cones and left cones topic
    topicr = b'0'
    topicl = b'1'
    socket.setsockopt(zmq.SUBSCRIBE, topicr)
    socket.setsockopt(zmq.SUBSCRIBE, topicl)


    # Keep listening to the topics
    while True:
        string = socket.recv()
        try:
            topic, x, y = string.split() 
            if topic == "0":
                right_points.append([x,y])
                #! HERE WE SHOULD ORDER POINTS AS WELL
            else:
                left_points.append([x,y])
            print(f"Topic: {topic} and point: ({x} , {y})")
        except ValueError:
            print(f"Received empty message for topic: {string}")

def user(right_points, left_points):
    my_r = []
    my_l = []
    while True: 
        lenr = len(right_points)
        lenl = len(left_points)
        if len(my_r) != lenr:
            my_r = right_points[:]
            print("Update my_r in USER!")
        if len(my_l) != lenl:
            my_l = left_points[:]
            print("Update my_l in USER!")


if __name__ == "__main__":
    manager = multiprocessing.Manager()
    right_points = manager.list()
    left_points = manager.list()


    p1 = multiprocessing.Process(target=receiver, args=(right_points, left_points, "5556"))
    p2 = multiprocessing.Process(target=user, args=(right_points, left_points))

    p1.start()
    p2.start()

    p1.join()
    p2.join()