import sys
import zmq
import os
import matplotlib.pyplot as plt
import random
import multiprocessing
import time
from utility_funcs import *



def order_point_list(list, first_point):
    """Orders a list of points based on proximity to the last ordered point.

    Args:
        list: A list of points.
        first_point: The point to start ordering from. Must be a member of the list.

    Returns:
        A new list with the points ordered based on proximity.
    """
    if first_point not in list:
        raise ValueError("first_point must be a member of the list")

    ordered_list = [first_point]
    remaining_points = list.copy()  # Create a copy to avoid modifying the original list
    remaining_points.remove(first_point)

    while remaining_points:
        closest_point = min(remaining_points, key=lambda point: euclidean_norm(ordered_list[-1], point))
        ordered_list.append(closest_point)
        remaining_points.remove(closest_point)

    return ordered_list


def order_both_lists_of_cones(rpoints, lpoints, reference_point):
    """Orders two lists of points (presumably right and left cones) based on 
    proximity and a dividing line defined by the first points of each list.

    Args:
        rpoints: The list of points for the right cones.
        lpoints: The list of points for the left cones.

    Returns:
        A list containing the two ordered lists of points, or an empty list if both input lists are empty.
        If only one list is empty, the other is ordered and returned along with an empty list.
    """
    if not rpoints and not lpoints:
        return []
    
    if not rpoints:
        return [[], order_point_list(lpoints, min(lpoints, key=lambda point: euclidean_norm(reference_point, point)))]
    
    if not lpoints:
        return [order_point_list(rpoints, min(rpoints, key=lambda point: euclidean_norm(reference_point, point))), []]

    p1r = min(rpoints, key=lambda point: euclidean_norm(reference_point, point))
    p1l = min(lpoints, key=lambda point: euclidean_norm(reference_point, point))

    rpoints = order_point_list(rpoints, p1r)
    lpoints = order_point_list(lpoints, p1l)

    return [rpoints, lpoints]


def compute_trajectory(rpoints, lpoints, start_point):
    """Computes the trajectory of the car by iteratively finding the midpoint between the next right and left cones.

    This function calculates the car's trajectory based on the positions of right and left cones. It iteratively identifies the next right or left cones and computes the midpoint between them. This midpoint serves as the next point in the trajectory. The algorithm considers the distances between cones to determine which cone to select next, ensuring a smooth and accurate trajectory.

    The function also handles cases where one side (right or left) has more cones than the other. In such scenarios, it continues to follow the remaining cones until all cones have been considered.

    Args:
        right_points (list): A list of coordinates representing the right cones. Already in order
        left_points (list): A list of coordinates representing the left cones. Already in order

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
    # Add first trajectory point
    #start_point = compute_midpoint(rpoints[0], lpoints[0])
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


        # In case 2 trajectory points are too close, remove them and take only the average point. This is done outside this function
    return mid_points

def merge_too_close_points(points, dist_tol=3.1):
    """Merges points in a list that are closer than a given distance tolerance. But does not merge more than 2 consecutive points.
    Does a second pass of merging so that it merges up to 3 or 4 consecutive points if they are still very very close to each other

    Args:
        points: A list of points, where each point is a list of coordinates [x, y].
        dist_tol: The distance tolerance below which points are merged.

    Returns:
        A new list of points with close points merged.
    """
    if not points:  # Handle empty list case
        return []

    if len(points) == 1:
        return points
    
    merged_points =[]
    i = 0
    while i < len(points) -1:
        if euclidean_norm(points[i], points[i+1]) <= dist_tol:
            merged_points.append(compute_midpoint(points[i], points[i + 1]))
            i +=2 # Skip the next point since it was already merged
        else:
            merged_points.append(points[i])
            i += 1

    if i == len(points) -1: # Add the last point if it wasn't merged
        merged_points.append(points[i])

    i = 0
    merged_points2 = []
    while i < len(merged_points) - 1:
        if euclidean_norm(merged_points[i], merged_points[i+1]) <= dist_tol/2:
            merged_points2.append(compute_midpoint(merged_points[i], merged_points[i + 1]))
            i += 2
        else:
            merged_points2.append(merged_points[i])
            i += 1
    if i == len(merged_points) - 1:
        merged_points2.append(merged_points[i])


    return merged_points2


def run_sub(port = "5556"):
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

    # Use a poller for keeping track of available messages
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    
    # Alternate listening to topics with computing the trajectory
    right_points = [[3, -2.5]] #Initial orange right cone
    left_points = [[3, 2.5]] #Initial orange left cone
    midpoints = [[3,0]] #This is the initial position of the car
    r = l = skipped = 0 #This is just for trimming the list of midpoints
    lim = 10 #Number of cones to keep.
    reference_point = midpoints[0]
    final_midpoints = []
    while True:
        print("USING THE POLLER TO GET ALL THE MESSAGES")
        socks = dict(poller.poll()) # Block indefinitely until a message arrives

        if socket in socks and socks[socket] == zmq.POLLIN:
            # Receive all available messages
            received_empty = True
            while True:
                try:
                    string = socket.recv(zmq.NOBLOCK)
                    topic, x, y = string.split()
                    if topic == b'0':
                        right_points.append([float(x), float(y)])
                    else:
                        left_points.append([float(x), float(y)])
                    print(f"Topic: {topic} and point: ({x} , {y})")
                    received_empty = False #Mark that we received a non-empty message
                except zmq.Again:
                    # No more messages in queue
                    break
                except ValueError:
                    print(f"Received empty message: {string}")
                    
            if received_empty:
                continue # Go back to the beginning of the outer loop and wait for more messages

        print("NOW WE ARE GOING TO DO THE CALCULATIONS")
        # Perform calculations AFTER processing all received messages.
        # To prevent the lists from getting too long, we will only keep track of the last 20 cones.
        if len(right_points)> lim:
            r += len(right_points) - lim
            right_points = right_points[-lim:]
        
        if len(left_points)> lim:
            l += len(left_points) - lim
            left_points = left_points[-lim:]
        if r > 0 or l > 0:
            print(f"{midpoints[0]} before trim")
            skip = min(r,l) #The number of points we are removing from midpoints
            final_midpoints.extend(midpoints[:skip-skipped])
            print(f"Skipped points: {skipped}")
            serialize_midpoints(final_midpoints, filename="midpoints", logs_folder="logs") #final midpoints are only added when we remove cones, so the rest of midpoints should be added at then end of execution, when no more new cones are detected.
            reference_point = midpoints[skip-skipped].copy()
            print(f"{midpoints[0]} after trim trim")
            print(f"Reference point: {reference_point}")
            skipped += skip - skipped
        
        right_points, left_points = order_both_lists_of_cones(right_points, left_points, reference_point)
               

        # In case we have already computed midpoints, we want to check whether the new points will change some midpoints or not and go back to where the midpoints might start changing so that we only recompute the trajectories that are different with new info, not the whole trajectories
        midpoints = compute_trajectory(right_points, left_points, reference_point)
        
        print(f"length of midpoints after computations is {len(midpoints)}")

        #To prevent points to be too close to each other we will do some merging: 
        right_points = merge_too_close_points(right_points, dist_tol = 3)
        left_points = merge_too_close_points(left_points, dist_tol = 3)
        merged_midpoints = merge_too_close_points(midpoints, dist_tol = 3.5)
        #print(f"midpoints after merge: {merged_midpoints}")

        # Serialize
        serialize_points(right_points, left_points, filename = "seenpoints", logs_folder="logs")
        serialize_midpoints(merged_midpoints, filename="midpoints", logs_folder="logs")




if __name__ == "__main__":
    run_sub(port="5556")