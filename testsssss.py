from utility_funcs import *

def gen_straight_line(init_pos, init_dir, width):
    length = random.randint(2, 8) * 10
    print(f"STRAIGHT LINE of length {length}m")
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
    else:#Case vertical line
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


init_pos1 = [20, -50]
init_dir1 = [0, 1]
width1 = 2
final_pos1, final_dir1, rpoints1, lpoints1 = gen_straight_line(init_pos1, init_dir1, width1)

init_pos2 = [30, 50]
init_dir2 = [0, -1]
width2 = 2
final_pos2, final_dir2, rpoints2, lpoints2 = gen_straight_line(init_pos2, init_dir2, width2)


import matplotlib.pyplot as plt
x1 = [p[0] for p in rpoints1]
y1 = [p[1] for p in rpoints1]
x2 = [p[0] for p in lpoints1]
y2 = [p[1] for p in lpoints1]

plt.plot(x1, y1, 'r*')
plt.plot(x2, y2, 'b*')

x1 = [p[0] for p in rpoints2]
y1 = [p[1] for p in rpoints2]
x2 = [p[0] for p in lpoints2]
y2 = [p[1] for p in lpoints2]

plt.plot(x1, y1, 'r*')
plt.plot(x2, y2, 'b*')

plt.show()

