import zmq
import os
import random
import sys
import time
from utility_funcs import *



def gen_straight_line(init_pos, init_dir, width):
    length = random.randint(2, 8) * 10
    final_pos = [init_pos[0] + length*init_dir[0], init_pos[1] + length*init_dir[1]]
    final_dir = init_dir

    w = width/2
    rpoints = []
    lpoints = []
    perp = get_perpendicular_vector(init_dir)
    #Case non vertical line
    if init_pos[0] != final_pos[0]:
        if init_pos[0] < final_pos[0]:
            x_values = random_partition(init_pos[0], final_pos[0], 3, 5)
        else:
            x_values = random_partition(final_pos[0], init_pos[0], 3, 5)
            x_values.reverse()

        line = get_line_function(compute_slope(init_pos, final_pos),init_pos)
        y_values = [line(x) for x in x_values]
    #Case vertical line
    else:
        if init_pos[1] < final_pos[1]:
            y_values = random_partition(init_pos[1], final_pos[1], 3, 5)
        else:
            y_values = random_partition(final_pos[1], init_pos[1], 3, 5)
            y_values.reverse()
        x_values = [init_pos[0]] * len(y_values)
    
    for x, y in zip(x_values, y_values):
        lnum = random.uniform(0, 0.15)
        lpoints.append([x + (w + lnum)*perp[0], y + (w + lnum)*perp[1]])
        
        rnum = random.uniform(0, 0.15)
        rpoints.append([x - (w + rnum)*perp[0], y - (w + rnum)*perp[1]])
    return final_pos, final_dir, rpoints, lpoints


def gen_turn(init_pos, init_dir, width):
    degree = random.choice([45, 90, 135, 180])
    orientation = random.choice([-1, 1]) #+1 left, -1 right
    if orientation > 0:
        print("LEFT TURN")
    else:
        print("RIGHT TURN")
    rad = random.randint(9, 25)
    final_dir = rotate_vector(init_dir, degree * orientation)
    
    # Get final position 
    rad_vect = get_perpendicular_vector(init_dir) #Unitary
    rad_vect = scalar_mul(rad_vect, orientation) #Pointing inwards
    aux = scalar_mul(rad_vect, rad) #Not unitary, pointing inwards
    centre = add(init_pos, aux)
    aux = scalar_mul(aux, -1) #Not unitary, pointing outwards
    aux = rotate_vector(aux, degree * orientation) #Not unitary
    final_pos = add(aux, centre)

    # Get points separated radomly between 1 and 4 meters.
    rad_vect = scalar_mul(rad_vect, -1) #Pointing outwards
    len_curve = angle_to_arc(degree, rad)
    part_curve = random_partition(0, len_curve, 1, 4)
    angles_curve = list(arc_to_angle(l, rad) * orientation for l in part_curve)
    rpoints, lpoints = [], []
    for a in angles_curve:
        vect = rotate_vector(rad_vect, a)
        innum = random.uniform(0, 0.1)
        vect_in = scalar_mul(vect, rad - width/2 + innum)
        outnum = random.uniform(0, 0.1)
        vect_out = scalar_mul(vect, rad + width/2 - outnum)

        if orientation > 0:
            rpoint = add(centre, vect_out)
            lpoint = add(centre, vect_in)
        else:
            rpoint = add(centre, vect_in)
            lpoint = add(centre, vect_out)

        rpoints.append(rpoint)
        lpoints.append(lpoint)

    return final_pos, final_dir, rpoints, lpoints

def remove_some_cones(og_right_points, og_left_points, skip_size=2):
    """Removes some cones from the original lists of right and left cones, keeping the first cone of each list.
       It uses a maximum skip_size for how many adjacent points it can remove. If 0, no points are removed

    Args:
        og_right_points (list): The original list of right cones.
        og_left_points (list): The original list of left cones.
        skip_size (int, optional): The maximum number of cones to skip. Defaults to 2.

    Returns:
        tuple: A tuple containing two lists: the new list of right cones and the new list of left cones.
    """
    right_points = [og_right_points[0]]  # Always keep the first right point
    left_points = [og_left_points[0]]    # Always keep the first left point
    
    right_idx = 1
    left_idx = 1
    
    while right_idx < len(og_right_points) or left_idx < len(og_left_points):
        # Handle right points
        if right_idx < len(og_right_points):
            skip = random.randint(0, skip_size)
            right_idx += skip
            if right_idx < len(og_right_points):
                right_points.append(og_right_points[right_idx])
            right_idx += 1
        
        # Handle left points
        if left_idx < len(og_left_points):
            skip = random.randint(0, skip_size)
            left_idx += skip
            if left_idx < len(og_left_points):
                left_points.append(og_left_points[left_idx])
            left_idx += 1
    
    return right_points, left_points


def permute_pairs(list1, list2):
    """Permutes or not the pairs of points in both lists.

    Args:
        list1: The first list of points.
        list2: The second list of points.

    Returns:
        A tuple containing the two lists after the permutations.
    """
    # Create copies of the lists to avoid modifying the originals
    list1_copy = list1.copy()
    list2_copy = list2.copy()

    # Iterate through the pairs of points
    for i in range(0, len(list1_copy) - 1, 2):
        # Decide whether to permute the pair
        if random.choice([True, False]):
            list1_copy[i], list1_copy[i+1] = list1_copy[i+1], list1_copy[i]
    
    for i in range(0, len(list2_copy) - 1, 2):
            
        if random.choice([True, False]):
            list2_copy[i], list2_copy[i+1] = list2_copy[i+1], list2_copy[i]

    return list1_copy, list2_copy


def perception_sender(socket, right_points, left_points):
    """Sends a random right or left point to the simulator."""
    while right_points or left_points:
        topic = random.choice([0, 1])
        # Topic 0 for right cones
        if topic == 0:
            if right_points:
                point = right_points.pop(0)
                messagedata = f"{point[0]} {point[1]}"
            else:
                messagedata = ""  # Handle case where right_points is empty
        # Topic 1 for left cones
        else:
            if left_points:
                point = left_points.pop(0)
                messagedata = f"{point[0]} {point[1]}"
            else:
                messagedata = ""  # Handle case where left_points is empty

        print("%d %s" % (topic, messagedata))
        socket.send_string("%d %s" % (topic, messagedata))
        time.sleep(random.uniform(0, 3))


def run_pub(port = "5556"):
    print("Starting the publisher...")

    #Set the port and binding it.
    if len(sys.argv) > 1:
        port =  sys.argv[1]
        int(port)

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port)
        
    # Start the loop
    init_pos = [3,0]
    init_dir = [1,0]
    first_iteration = True
    while True:
        if first_iteration:
            width = 5 #First part of the track matches the initial box width
            first_iteration = False
        else:
            width_increment = random.choice([0.5, -0.5])
            if width + width_increment > 6 or width + width_increment < 3:
                width_increment = -1 * width_increment
            width = width + width_increment  # Random width between 3 and 6 that changes "smoothly"

        if random.choice([True, False]):  # Randomly choose between straight line and turn
            aux = init_pos[:]
            init_pos, init_dir, rpoints, lpoints = gen_straight_line(init_pos, init_dir, width)
        else:
            init_pos, init_dir, rpoints, lpoints = gen_turn(init_pos, init_dir, width) 

        og_right_points = rpoints[1:]
        og_left_points = lpoints[1:]
        serialize_points(og_right_points, og_left_points, filename = "ogpoints", logs_folder="logs")
        # Change the skip_size to randomly remove more or less consecutive points
        right_points, left_points = remove_some_cones(og_right_points, og_left_points, skip_size=2)
        # Disorder cones
        right_points, left_points = permute_pairs(right_points, left_points)
        #Sending logic
        perception_sender(socket, right_points, left_points)




if __name__ == "__main__":
    run_pub(port = "5556")

    