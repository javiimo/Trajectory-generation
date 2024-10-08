import random
from utility_funcs import *
import matplotlib.pyplot as plt



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
    print("Centre at ", centre)
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

    return final_pos, final_dir, rpoints, lpoints, centre

def plot_initial_box(initial_box):
    """Plots the initial box in orange."""
    x_coords = [point[0] for point in initial_box]
    y_coords = [point[1] for point in initial_box]
    plt.scatter(x_coords, y_coords, color='orange')

def plot_track(initial_box, final_pos, final_dir, rpoints, lpoints, centre):
    """Plots the generated track."""
    plot_initial_box(initial_box)
    # Plot rpoints in yellow and lpoints in blue
    plt.scatter([p[0] for p in rpoints], [p[1] for p in rpoints], color='yellow', label='rpoints')
    plt.scatter([p[0] for p in lpoints], [p[1] for p in lpoints], color='blue', label='lpoints')

    # Plot final_pos in black
    plt.scatter(final_pos[0], final_pos[1], color='black', label='final_pos')

    # Plot final_dir as an arrow in black
    plt.arrow(final_pos[0], final_pos[1], final_dir[0], final_dir[1], head_width=0.5, head_length=0.7, fc='black', ec='black')
    
    # Plot centre in red
    plt.scatter(centre[0], centre[1], color='red', label='centre')


    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Generated Track')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')  # Ensure equal aspect ratio
    plt.xlim(centre[0] - 40, centre[0] + 40)  # Set x-axis limits
    plt.ylim(centre[1] - 40, centre[1] + 40)  # Set y-axis limits
    plt.show(block=False)
    plt.pause(2) #Wait for 2 seconds


if __name__ == "__main__":
    initial_box = [[3, -2.5], [3, 2.5], [-3, -2.5], [-3, 2.5 ]]

    init_pos = [3,0]
    init_dir = [1,0]
    # Example usage:
    
    plot_initial_box(initial_box)
    all_rpoints = []
    all_lpoints = []

    first_iteration = True
    while True:  # Generate infinite tracks

        if first_iteration:
            width = 5 #First part of the track matches the initial box width
            first_iteration = False
        else:
            width = random.uniform(3, 6)  # Random width between 3 and 6

        if random.choice([True, False]):  # Randomly choose between straight line and turn
            aux = init_pos[:]
            init_pos, init_dir, rpoints, lpoints = gen_straight_line(init_pos, init_dir, width)
            centre = compute_midpoint(aux, init_pos)
        else:
            init_pos, init_dir, rpoints, lpoints, centre = gen_turn(init_pos, init_dir, width) 

        all_rpoints.extend(rpoints[1:])
        all_lpoints.extend(lpoints[1:])

        plot_track(initial_box, init_pos, init_dir, all_rpoints, all_lpoints, centre)
        plt.close()
