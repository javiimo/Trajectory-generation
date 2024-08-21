import math
import random
import matplotlib.pyplot as plt


# This script generates a track defined by cone coordinates.
#
# The track starts at (0, 0) pointing in the positive x axis and consists of:
#   - A 90-degree right turn
#   - A 90-degree left turn
#   - A straight section
#
# Each turn is composed of 5 pairs of cones and has a minimum competition radius of 9m (inner) with a 3m track width.
#
# The straight section is 80m long and features a slalom with:
#   - Cone spacing between 7.5m and 12m
#   - Track width randomly varying between 3m and 5m

# It also generates a circular map with a certain radius and a certain number of cones, but that is a different file and a different function generator.



angles_first_curve = (90, 67.5, 45, 22.5, 0)
angles_second_curve = (-157.5, -135, -112.5, -90)
center_first_curve = [0, -10.5]
center_second_curve = [21, -10.5]
inner_rad = 9
external_rad = 12
straight_line_begining = [21, -21]
straight_line_end = [101, -21]

def get_curve_points(a, b, radius, angle_degrees):
    
    angle_radians = math.radians(angle_degrees)
    x = a + radius * math.cos(angle_radians)
    y = b + radius * math.sin(angle_radians)
    
    return [x, y]

def get_first_curve():
    
    in_points = []
    ext_points = []

    # Inner curve:
    for a in angles_first_curve:
        in_points.append(get_curve_points(center_first_curve[0], 
                                    center_first_curve[1], 
                                    inner_rad, a))
    
    for a in angles_first_curve:
        ext_points.append(get_curve_points(center_first_curve[0], 
                                 center_first_curve[1], 
                                 external_rad, a))
        
    return {'first_curve_r': in_points, 'first_curve_l': ext_points}

def get_second_curve():
    
    in_points = []
    ext_points = []

    # Inner curve:
    for a in angles_second_curve:
        in_points.append(get_curve_points(center_second_curve[0], 
                                    center_second_curve[1], 
                                    inner_rad, a))
    
    for a in angles_second_curve:
        ext_points.append(get_curve_points(center_second_curve[0], 
                                 center_second_curve[1], 
                                 external_rad, a))
        
    return {'second_curve_r': ext_points, 'second_curve_l': in_points}

def random_partition(start, end, min_distance, max_distance):
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

def get_straight_path():
    x_coords = random_partition(straight_line_begining[0], straight_line_end[0], min_distance=7.5, max_distance=12)

    r_points = []
    l_points = []

    for x in x_coords[1:]:
        ry = straight_line_begining[1] - 1.5 - 1 * random.uniform(0, 1)
        ly = straight_line_begining[1] + 1.5 + 1 * random.uniform(0, 1)
        r_points.append([x, ry])
        l_points.append([x, ly])

    return {'straight_r': r_points, 'straight_l': l_points}
    

def gen_map(filename: str = None, plot: bool = True):
    map = {}
    map.update(get_first_curve())
    map.update(get_second_curve())
    map.update(get_straight_path())

    try:
        if filename is not None:
            with open(filename, 'w') as f:
                # Write right points
                f.write("RIGHT_POINTS\n")
                for key in map:
                    if key.endswith('_r'):
                        for point in map[key]:
                            f.write(f"{point[0]} {point[1]}\n")
                
                # Write left points
                f.write("LEFT_POINTS\n")
                for key in map:
                    if key.endswith('_l'):
                        for point in map[key]:
                            f.write(f"{point[0]} {point[1]}\n")
            print("Successfully serialized the map points into " + filename)
        else:
            print("No filename given for serializing")

    except Exception as e:
        print(f"Exception occurred: {e}")
        print("Did not serialize the map")
        

    finally:
        print("Plotting the map")
        if plot:
            # Create a set to track added labels so that they don't repeat
            added_labels = set()

            # Plot right points in yellow
            for key in map:
                if key.endswith('_r'):
                    x, y = zip(*map[key])
                    plt.scatter(x, y, color='yellow', label='Right Points' if 'Right Points' not in added_labels else "")
                    added_labels.add('Right Points')

            # Plot left points in blue
            for key in map:
                if key.endswith('_l'):
                    x, y = zip(*map[key])
                    plt.scatter(x, y, color='blue', label='Left Points' if 'Left Points' not in added_labels else "")
                    added_labels.add('Left Points')

            plt.xlabel('X')
            plt.ylabel('Y')
            plt.title('Map Points')
            plt.grid(True)
            plt.axis('equal')
            plt.legend()
            plt.show()

def gen_circular_map(radius: float, num_cones: int, filename: str = None, plot: bool = True):
    """Generates a circular map with the given radius and number of cones."""
    map = {'circular_r': [], 'circular_l': []}
    
    angle_increment = 360.0 / num_cones

    for i in range(num_cones):
        angle_degrees = i * angle_increment
        angle_radians = math.radians(angle_degrees)
        
        # Inner cones
        x_inner = radius * math.cos(angle_radians)
        y_inner = radius * math.sin(angle_radians)
        map['circular_r'].append([x_inner, y_inner])
        
        # Outer cones (slightly further out)
        x_outer = (radius + 3) * math.cos(angle_radians)
        y_outer = (radius + 3) * math.sin(angle_radians)
        map['circular_l'].append([x_outer, y_outer])

    try:
        if filename is not None:
            with open(filename, 'w') as f:
                # Write right points
                f.write("RIGHT_POINTS\n")
                for point in map['circular_r']:
                    f.write(f"{point[0]} {point[1]}\n")
                
                # Write left points
                f.write("LEFT_POINTS\n")
                for point in map['circular_l']:
                    f.write(f"{point[0]} {point[1]}\n")
            print("Successfully serialized the map points into " + filename)
        else:
            print("No filename given for serializing")

    except Exception as e:
        print(f"Exception occurred: {e}")
        print("Did not serialize the map")

    finally:
        print("Plotting the map")
        if plot:
            # Plot right points in yellow
            x, y = zip(*map['circular_r'])
            plt.scatter(x, y, color='yellow', label='Right Points')

            # Plot left points in blue
            x, y = zip(*map['circular_l'])
            plt.scatter(x, y, color='blue', label='Left Points')

            plt.xlabel('X')
            plt.ylabel('Y')
            plt.title('Map Points')
            plt.grid(True)
            plt.axis('equal')
            plt.legend()
            plt.show()


if __name__ == "__main__":
    random.seed(3)  # Set a seed for the random numbers
    filename = input("Please enter the filename to save the map points: ")
    if filename == '':
        filename = None #This does not save it, only plot it
    if filename is not None and "." not in filename:
        filename = filename + ".dat"
    gen_map(filename)

    # Also create a circular map file
    circular_filename = input("Please enter the filename to save the circular map points: ")
    if circular_filename == '':
        circular_filename = None #This does not save it, only plot it
    if circular_filename is not None and "." not in circular_filename:
        circular_filename = circular_filename + ".dat"
    gen_circular_map(radius=20, num_cones=20, filename=circular_filename)
