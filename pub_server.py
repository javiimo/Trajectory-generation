import zmq
import os
import random
import sys
import time


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


#! This might be too much, it is very unlikely the car sees accurately a cone too far.
def disorder_points(list1, list2):
    """Disorders two lists of points (except for the first point of each list).

    Args:
        list1: The first list of points.
        list2: The second list of points.

    Returns:
        A tuple containing the two disordered lists.
    """
    # Create copies of the lists to avoid modifying the originals
    list1_copy = list1.copy()
    list2_copy = list2.copy()

    # Shuffle the lists from the second element onwards
    random.shuffle(list1_copy[1:])
    random.shuffle(list2_copy[1:])

    return list1_copy, list2_copy


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





if __name__ == "__main__":
    #Set the port and binding it.
    port = "5556"
    if len(sys.argv) > 1:
        port =  sys.argv[1]
        int(port)

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port)

    #Opening the data points file
    filename = ''
    while filename == '':
        filename = input("Please enter the filename to load the map points: ")
        if not os.path.exists(filename):
            print("File does not exist. Please enter a valid filename.")
            filename = ''
        
    og_right_points, og_left_points = deserialize_points(file_path=filename)
    # Change the skip_size to randomly remove more or less consecutive points
    right_points, left_points = remove_some_cones(og_right_points, og_left_points, skip_size=2)
    right_points, left_points = permute_pairs(right_points, left_points)
    
    #Sending logic
    while True:
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