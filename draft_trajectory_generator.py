import os
import matplotlib.pyplot as plt
import random

def deserialize_points(file_path="map.dat"):
    right_points = []
    left_points = []
    
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
    
    return right_points, left_points


def compute_slope(p1, p2):
    if abs(p1[0] - p2[0]) < 1e-12:  # Check for vertical line with a small threshold
        return float('inf') if p2[1] > p1[1] else -float('inf')
    return (p2[1] - p1[1]) / (p2[0] - p1[0])


def compute_midpoint(p1, p2):
    return [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]


def euclidean_norm(p1, p2):
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5


def scalar_prod(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1]


def compute_vector(p_i, p_f):
    return [p_f[0]-p_i[0], p_f[1]-p_i[1]]


def rotate_180(vector):
    return [-vector[0], -vector[1]]


def get_line_function(slope, point):
    x1, y1 = point
    def line_function(x):
        return slope * (x - x1) + y1
    return line_function


def is_clockwise(vector1, vector2):
    """
    Determine if the rotation from vector1 to vector2 is clockwise.

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
    # Unpack the points
    x1, y1 = point1
    x2, y2 = point2

    # Check if the slopes are the same (parallel lines)
    if abs(slope1 - slope2) < 1e-10:
        return None  # No intersection (or infinite intersections if they are the same line)

    # Calculate the intersection x-coordinate
    x = (y2 - y1 + slope1 * x1 - slope2 * x2) / (slope1 - slope2)

    # Calculate the intersection y-coordinate using the equation of the first line
    y = slope1 * x + (y1 - slope1 * x1)

    return [x, y]



def compute_trajectory(right_points, left_points, threshold = 1.5):
    start = compute_midpoint(right_points[0], left_points[0])
    mid_points = [start]
    # In case each list of points wasn't ordered we could sort it using the euclidean norm here.
    
    right_slopes = []
    for i in range(len(right_points)-1):
        right_slopes.append(compute_slope(right_points[i], right_points[i+1]))

    left_slopes = []
    for i in range(len(left_points)-1):
        left_slopes.append(compute_slope(left_points[i], left_points[i+1]))

    last_ri = 0 #index for right points
    last_li = 0 #index for left points
    final_slopes = [0] #Because it starts looking in the positive x direction
    i = 0 #index for computing the intersection
    extra_added = 0
    while last_ri<len(right_points)-1 and last_li<len(left_points)-1:
        # Compute distances to detect missed cones
        # Same Side
        e1 = euclidean_norm(right_points[last_ri], right_points[last_ri+1]) #Right border length
        e2 = euclidean_norm(left_points[last_li], left_points[last_li+1]) #Left border length

        # Check if one side is left behind too much
        if 1.2 * euclidean_norm(mid_points[-1],right_points[last_ri]) < euclidean_norm(mid_points[-1],right_points[last_ri+1]):
            last_ri += 1
        
        if 1.2 * euclidean_norm(mid_points[-1],left_points[last_li]) < euclidean_norm(mid_points[-1], left_points[last_li+1]):
            last_li += 1

        if e1/e2 > threshold and last_ri<len(right_points)-1 and last_li<len(left_points)-1: #Right border much longer
            slope = left_slopes[last_li]
            last_li += 1
        elif e2/e1 > threshold and last_ri<len(right_points)-1 and last_li<len(left_points)-1: #Left border much longer
            slope = right_slopes[last_ri]
            last_ri += 1
        elif last_ri<len(right_points)-1 and last_li<len(left_points)-1:
            slope = (left_slopes[last_li] + right_slopes[last_ri])/2
            last_li += 1
            last_ri += 1
            extra_point = compute_midpoint(compute_midpoint(right_points[last_ri-1], left_points[last_li]), 
                                           compute_midpoint(right_points[last_ri], left_points[last_li-1]))
            mid_points.append(extra_point)
            extra_added +=1
        else:
            break

        final_slopes.append(slope)
        last_point = compute_midpoint(right_points[last_ri], left_points[last_li])
        intersection = find_intersection(final_slopes[i], mid_points[2*i+extra_added], final_slopes[i+1], last_point)
        

        if intersection is None:
            mid_points.append([])
        elif euclidean_norm(intersection, mid_points[2*i+extra_added]) > euclidean_norm(mid_points[2*i+extra_added], last_point) or euclidean_norm(intersection, last_point) > euclidean_norm(mid_points[2*i+extra_added], last_point):
            mid_points.append([])
        else:
            mid_points.append(intersection)
        mid_points.append(last_point)
        i += 1
    mid_points.append(compute_midpoint(right_points[-1], left_points[-1]))
        
    
    return mid_points


def order_point_list(list):
    #! Add a way to take as second points the ones in the semiplane ahead of the car
    # Assume the first point is still the first point
    ordered_list = [list[0]] #Assume the first point is ordered correctly
    remaining_points = list[1:]
    
    while remaining_points:
        closest_point = min(remaining_points, key=lambda point: euclidean_norm(ordered_list[-1], point))
        ordered_list.append(closest_point)
        remaining_points.remove(closest_point)
    
    return ordered_list


def compute_trajectory2(right_points, left_points):
    # Assert the points are correctly ordered
    rpoints = order_point_list(right_points)
    lpoints = order_point_list(left_points)

    start_point = compute_midpoint(rpoints[0], lpoints[0])
    mid_points = [start_point]

    last_ri = 0
    last_li = 0
    while last_ri<len(right_points)-1 and last_li<len(left_points)-1:
        if last_ri!=len(right_points)-1 and last_li!=len(left_points)-1:
            distr = euclidean_norm(rpoints[last_ri], rpoints[last_ri+1]) + euclidean_norm(lpoints[last_li], rpoints[last_ri+1])
            distl = euclidean_norm(lpoints[last_li], lpoints[last_li+1]) + euclidean_norm(rpoints[last_ri], lpoints[last_li+1])

        if distr<=distl or last_li == len(left_points)-1:
            last_ri +=1
            last_cone = rpoints[last_ri]
            other_last_cone = lpoints[last_li]
            slope = compute_slope(rpoints[last_ri-1], last_cone)
        else:
            last_li +=1
            last_cone = lpoints[last_li]
            other_last_cone = rpoints[last_ri]
            slope = compute_slope(lpoints[last_li-1], last_cone)

        perp_slope = - 1 / slope
        new_point = find_intersection(slope, mid_points[-1], perp_slope, last_cone)

        #In case the new point is too close or too far to the last cone
        if euclidean_norm(new_point, last_cone) != 1.5:
            vector = [new_point[0]-last_cone[0], new_point[1]-last_cone[1]]
            norm = euclidean_norm(vector, [0,0])
            vector = [1.5 * vector[0]/norm, 1.5 * vector[1]/norm]
            new_point2 = [last_cone[0] + vector[0], last_cone[1] + vector[1]]
            new_point = new_point2
            print(f"Too close last ri:{last_ri}, last_li: {last_li}")
            
            # Trying to prevent getting outside
            if euclidean_norm(new_point, other_last_cone)< euclidean_norm(new_point2, other_last_cone):
                new_point = [ - new_point2[0], - new_point2[1]]
                print("Taking mid point instead")
            

        mid_points.append(new_point)
        print(f"End iteration last ri:{last_ri}, last_li: {last_li}")


    return mid_points


def compute_trajectory2_wsteps_circ(right_points, left_points):
    # Assert the points are correctly ordered
    rpoints = order_point_list(right_points)
    lpoints = order_point_list(left_points)

    # Add first trajectory point
    start_point = compute_midpoint(rpoints[0], lpoints[0])
    mid_points = [start_point]

    # Auxiliary variables
    last_ri = 0
    last_li = 0
    rotated = False
    # Main loop
    while last_ri < len(rpoints) - 1 or last_li < len(lpoints) - 1:
        if last_ri < len(rpoints) - 1 and last_li < len(lpoints) - 1:
            distr = euclidean_norm(rpoints[last_ri], rpoints[last_ri+1]) + euclidean_norm(lpoints[last_li], rpoints[last_ri+1])
            distl = euclidean_norm(lpoints[last_li], lpoints[last_li+1]) + euclidean_norm(rpoints[last_ri], lpoints[last_li+1])
        elif last_ri < len(rpoints) - 1:
            distr = 0  # Force right side movement
            distl = float('inf')
        else:
            distr = float('inf')
            distl = 0  # Force left side movement

        if distr <= distl:
            last_ri += 1
            last_cone = rpoints[last_ri]
            other_last_cone = lpoints[last_li]
            slope = compute_slope(rpoints[last_ri-1], last_cone)
            # For plotting
            p1 = rpoints[last_ri-1]
            p2 = last_cone
        else:
            last_li += 1
            last_cone = lpoints[last_li]
            other_last_cone = rpoints[last_ri]
            slope = compute_slope(lpoints[last_li-1], last_cone)
            # For plotting
            p1 = lpoints[last_li-1]
            p2 = last_cone
        
        print(f"last ri:{last_ri}, last_li: {last_li}")

        perp_slope = - 1 / slope
        new_point = find_intersection(slope, mid_points[-1], perp_slope, last_cone)

        #In case the new point is too close or too far to the last cone
        if euclidean_norm(new_point, last_cone) != 1.5:
            vector = compute_vector(last_cone, new_point)
            norm = euclidean_norm(vector, [0,0])
            vector = [1.5 * vector[0]/norm, 1.5 * vector[1]/norm]
            new_point2 = [last_cone[0] + vector[0], last_cone[1] + vector[1]]
            new_point = new_point2
            print(f"Too close to last cone, separating to 1.5")
            
        # Trying to prevent getting outside with circunferences
        if euclidean_norm(other_last_cone, last_cone) < 0.95 * euclidean_norm(other_last_cone ,new_point):
            vector = compute_vector(last_cone, new_point)
            vector = rotate_180(vector)
            # Plot the circles
            circle1 = plt.Circle(other_last_cone, euclidean_norm(other_last_cone, last_cone), color='black', fill=False)
            circle2 = plt.Circle(other_last_cone, euclidean_norm(other_last_cone, new_point), color='red', fill=False)
            prev_rot = new_point
            rotated = True

            new_point = [last_cone[0] + vector[0], last_cone[1] + vector[1]]
            print('Rotated 180º')

            
            

        mid_points.append(new_point)

        # Order last 3 trajectory points (not needed in most cases, just a safety check)
        if len(mid_points)>=3:
            mid_points[-3:] = order_point_list(mid_points[-3:])

        # In case 2 trajectory points are too close, remove them and take the only midpoint
        if euclidean_norm(mid_points[-1], mid_points[-2]) < 2 :
            mid_point = [(mid_points[-1][0] + mid_points[-2][0])/2, (mid_points[-1][1] + mid_points[-2][1])/2]
            mid_points[-2:] = [mid_point]
            print(f"Removed 2 close points and replaced with midpoint")

        plt.clf()
        if rotated:
            plt.gca().add_patch(circle1)
            plt.gca().add_patch(circle2)
            plt.scatter([prev_rot[0]], [prev_rot[1]], c='k')
            rotated = False
        plt.scatter([p[0] for p in lpoints], [p[1] for p in lpoints], c='b', label='Left cones')
        plt.scatter([p[0] for p in rpoints], [p[1] for p in rpoints], c='yellow', label='Right cones')
        plt.scatter([p[0] for p in mid_points], [p[1] for p in mid_points], c='g', label='Mid points')
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], c='k', label='Last segment')
        plt.plot([p2[0], new_point[0]], [p2[1], new_point[1]], c='r', label='Perpendicular line')
        plt.legend()
        plt.waitforbuttonpress()

    plt.show()
    return mid_points



def compute_trajectory2_wsteps_slopes(right_points, left_points):
    # Assert the points are correctly ordered
    rpoints = order_point_list(right_points)
    lpoints = order_point_list(left_points)

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
        elif last_ri < len(rpoints) - 1:
            distr = 0  # Force right side movement
            distl = float('inf')
        else:
            distr = float('inf')
            distl = 0  # Force left side movement

        if distr <= distl:
            last_ri += 1
            last_cone = rpoints[last_ri]
            other_last_cone = lpoints[last_li]
            anchor_slope = rpoints[last_ri-1]
            slope = compute_slope(anchor_slope, last_cone)
            other_slope = compute_slope(anchor_slope, other_last_cone)
            # For plotting
            p1 = rpoints[last_ri-1]
            p2 = last_cone
        else:
            last_li += 1
            last_cone = lpoints[last_li]
            other_last_cone = rpoints[last_ri]
            anchor_slope = lpoints[last_li-1]
            slope = compute_slope(anchor_slope, last_cone)
            other_slope = compute_slope(anchor_slope, other_last_cone)
            # For plotting
            p1 = lpoints[last_li-1]
            p2 = last_cone
        
        print(f"last ri:{last_ri}, last_li: {last_li}")

        perp_slope = - 1 / slope
        new_point = find_intersection(slope, mid_points[-1], perp_slope, last_cone)

        #In case the new point is too close or too far to the last cone
        if euclidean_norm(new_point, last_cone) != 1.5:
            vector = compute_vector(last_cone, new_point)
            norm = euclidean_norm(vector, [0,0])
            vector = [1.5 * vector[0]/norm, 1.5 * vector[1]/norm]
            new_point2 = [last_cone[0] + vector[0], last_cone[1] + vector[1]]
            new_point = new_point2
            print(f"Too close to last cone, separating to 1.5")
            
        # Trying to prevent getting outside with slopes
        slope_list = [slope, other_slope] if slope < other_slope else [other_slope, slope]
        cond = compute_slope(anchor_slope, new_point) > slope_list[0] and compute_slope(anchor_slope, new_point) < slope_list[1]
        if cond == False:
            vector = compute_vector(last_cone, new_point)
            vector = rotate_180(vector)
            new_point = [last_cone[0] + vector[0], last_cone[1] + vector[1]]
            print('Rotated 180º')

        mid_points.append(new_point)

        # Order last 3 trajectory points (not needed in most cases, just a safety check)
        if len(mid_points)>=3:
            mid_points[-3:] = order_point_list(mid_points[-3:])

        # In case 2 trajectory points are too close, remove them and take the only midpoint
        if euclidean_norm(mid_points[-1], mid_points[-2]) < 2 :
            mid_point = [(mid_points[-1][0] + mid_points[-2][0])/2, (mid_points[-1][1] + mid_points[-2][1])/2]
            mid_points[-2:] = [mid_point]
            print(f"Removed 2 close points and replaced with midpoint")

        plt.clf()
        plt.scatter([p[0] for p in lpoints], [p[1] for p in lpoints], c='b', label='Left cones')
        plt.scatter([p[0] for p in rpoints], [p[1] for p in rpoints], c='yellow', label='Right cones')
        plt.scatter([p[0] for p in mid_points], [p[1] for p in mid_points], c='g', label='Mid points')
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], c='k', label='Last segment')
        plt.plot([p2[0], new_point[0]], [p2[1], new_point[1]], c='r', label='Perpendicular line')
        plt.legend()
        plt.waitforbuttonpress()

    plt.show()
    return mid_points


def compute_trajectory2_wsteps_clockwise(right_points, left_points):
    # Assert the points are correctly ordered
    rpoints = order_point_list(right_points)
    lpoints = order_point_list(left_points)

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
            # For plotting
            p1 = rpoints[last_ri-1]
            p2 = last_cone
        else:
            right = False
            last_li += 1
            last_cone = lpoints[last_li]
            other_last_cone = rpoints[last_ri]
            anchor_slope = lpoints[last_li-1]
            slope = compute_slope(anchor_slope, last_cone)
            # For plotting
            p1 = lpoints[last_li-1]
            p2 = last_cone
        
        print(f"last ri:{last_ri}, last_li: {last_li}")

        perp_slope = - 1 / slope
        new_point = find_intersection(slope, mid_points[-1], perp_slope, last_cone)

        #In case the new point is too close or too far to the last cone
        if euclidean_norm(new_point, last_cone) != 1.5:
            vector = compute_vector(last_cone, new_point)
            norm = euclidean_norm(vector, [0,0])
            vector = [1.5 * vector[0]/norm, 1.5 * vector[1]/norm]
            new_point = [last_cone[0] + vector[0], last_cone[1] + vector[1]]
            print(f"Too close to last cone, separating to 1.5")
            
        # Trying to prevent getting outside with counter-clockwise or clokwise:
        cond = is_clockwise(compute_vector(other_last_cone, last_cone), compute_vector(other_last_cone, new_point))
        if cond is not None: 
            cond = cond if right else not cond
            if cond == True:
                vector = compute_vector(last_cone, new_point)
                vector = rotate_180(vector)
                new_point = [last_cone[0] + vector[0], last_cone[1] + vector[1]]
                print('Rotated 180º')

        mid_points.append(new_point)

        # Order last 3 trajectory points (not needed in most cases, just a safety check)
        if len(mid_points)>=3:
            mid_points[-3:] = order_point_list(mid_points[-3:])

        # In case 2 trajectory points are too close, remove them and take the only midpoint
        if euclidean_norm(mid_points[-1], mid_points[-2]) < 2 :
            mid_point = [(mid_points[-1][0] + mid_points[-2][0])/2, (mid_points[-1][1] + mid_points[-2][1])/2]
            mid_points[-2:] = [mid_point]
            print(f"Removed 2 close points and replaced with midpoint")

        plt.clf()
        plt.scatter([p[0] for p in lpoints], [p[1] for p in lpoints], c='b', label='Left cones')
        plt.scatter([p[0] for p in rpoints], [p[1] for p in rpoints], c='yellow', label='Right cones')
        plt.scatter([p[0] for p in mid_points], [p[1] for p in mid_points], c='g', label='Mid points')
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], c='k', label='Last segment')
        plt.plot([p2[0], new_point[0]], [p2[1], new_point[1]], c='r', label='Perpendicular line')
        plt.legend()
        plt.waitforbuttonpress()

    plt.show()
    return mid_points



def plot_trajectory_and_cones(mid_points, right_points, left_points, og_right_points, og_left_points):
    # Plot mid_points as a black line
    x, y = zip(*[point for point in mid_points if point])  # Filter out empty points
    plt.plot(x, y, 'k-', label='Trajectory')

    # Plot midpoints as green scatter points
    plt.scatter(x, y, c='g', label='Midpoints')

    # Plot right_points and left_points in red
    all_detected = right_points + left_points
    x, y = zip(*all_detected)
    plt.scatter(x, y, c='r', label='Detected cones')

    # Plot undetected cones in blue
    undetected = [p for p in og_right_points + og_left_points if p not in all_detected]
    if undetected:
        x, y = zip(*undetected)
        plt.scatter(x, y, c='b', label='Undetected cones')

    plt.legend()
    plt.axis('equal')
    plt.show()


def remove_some_cones(og_right_points, og_left_points, skip_size=2):
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



if __name__ == "__main__":
    filename = 'circ_map.dat'
    while filename == '':
        filename = input("Please enter the filename to load the map points: ")
        if not os.path.exists(filename):
            print("File does not exist. Please enter a valid filename.")
            filename = ''
    
    og_right_points, og_left_points = deserialize_points(file_path=filename)
    right_points, left_points = remove_some_cones(og_right_points, og_left_points, skip_size=0)
    right_points, left_points = disorder_points(right_points, left_points)
    # mid_points = compute_trajectory(right_points, left_points, threshold = 1.5)
    # mid_points = compute_trajectory2(right_points, left_points)
    # mid_points = compute_trajectory2_wsteps_slopes(right_points, left_points)
    # mid_points = compute_trajectory2_wsteps_circ(right_points, left_points)
    mid_points = compute_trajectory2_wsteps_clockwise(right_points, left_points)
    plot_trajectory_and_cones(mid_points, right_points, left_points, og_right_points, og_left_points)
    