from utility_funcs import *
import time
import os
import matplotlib.pyplot as plt
import time


def plot_initial_box(initial_box = [[3, -2.5], [3, 2.5], [-3, -2.5], [-3, 2.5 ]]):
    """Plots the initial box in orange."""
    x_coords = [point[0] for point in initial_box]
    y_coords = [point[1] for point in initial_box]
    plt.scatter(x_coords, y_coords, color='orange')


def plot_trajectory_and_cones(mid_points=None, right_points=None, left_points=None, og_right_points=None, og_left_points=None, plot_initial_box_flag=False):
    """Plots the trajectory, detected cones, and undetected cones.

    Args:
        mid_points (list): List of midpoints of the trajectory.
        right_points (list): List of detected right cones.
        left_points (list): List of detected left cones.
        og_right_points (list): List of original right cones.
        og_left_points (list): List of original left cones.
        plot_initial_box_flag (bool): Whether to plot the initial box.
    """
    plt.close('all') # Close all existing figures
    fig, ax = plt.subplots() # Create a new figure and axes for each plot

    if plot_initial_box_flag:
        plot_initial_box() # Plot initial box only once

    # Plot mid_points if available
    if mid_points:
        x, y = zip(*[point for point in mid_points if point])  # Filter out empty points
        ax.plot(x, y, 'k-', label='Trajectory')
        ax.scatter(x, y, c='g', label='Midpoints')

    # Plot detected cones if available
    all_detected = right_points + left_points if right_points and left_points else right_points if right_points else left_points if left_points else None # Combine detected points if available
    if all_detected:
        x, y = zip(*all_detected)
        ax.scatter(x, y, c='r', label='Detected cones')

    # Plot undetected cones if available
    if og_right_points and og_left_points: # Only plot undetected if original points are available
        undetected = [p for p in og_right_points + og_left_points if all_detected is None or p not in all_detected]
        if undetected:
            x, y = zip(*undetected)
            ax.scatter(x, y, c='b', label='Undetected cones')

    ax.legend()
    ax.axis('equal')

    plt.draw() # Draw the plot
    plt.pause(0.001) # Pause to allow the plot to update


def plotter(logs_folder="logs"):
    """
    Plots data from files in the logs folder, matching timestamps between midpoints, seenpoints, and ogpoints.
    """
    plot_initial_box_flag = True

    try:
        files = os.listdir(logs_folder)
        
        # Group files by name and sort by timestamp
        file_groups = {}
        for file in files:
            try:
                if "_" in file and "." in file:
                    name, timestamp_str = file.split("_", 1)
                    timestamp_str = timestamp_str.split(".")[0]
                    timestamp = int(timestamp_str)
                    file_groups.setdefault(name, []).append((timestamp, file))
                else:
                    print(f"Skipping invalid filename format: {file}")

            except ValueError:
                print(f"Skipping invalid filename format: {file}")

        # Sort files within each group by timestamp
        for name in file_groups:
            file_groups[name].sort(key=lambda x: x[0])

        # Assuming 'midpoints' and 'seenpoints' have the same number of files
        midpoints_files = file_groups.get("midpoints", [])
        seenpoints_files = file_groups.get("seenpoints", [])
        ogpoints_files = file_groups.get("ogpoints", [])

        # Iterate through midpoints and seenpoints, finding matching or previous ogpoints
        for i in range(len(midpoints_files)):
            midpoints_timestamp, midpoints_file = midpoints_files[i]
            seenpoints_timestamp, seenpoints_file = seenpoints_files[i]

            try:
                mid_points = deserialize_midpoints(os.path.join(logs_folder, midpoints_file))
                right_points, left_points = deserialize_points(os.path.join(logs_folder, seenpoints_file))

                # Find closest ogpoints file
                og_right_points, og_left_points = None, None
                closest_og_timestamp = -1
                for og_timestamp, og_file in ogpoints_files:
                    if og_timestamp <= midpoints_timestamp and og_timestamp > closest_og_timestamp:
                        closest_og_timestamp = og_timestamp
                        try:
                            og_right_points, og_left_points = deserialize_points(os.path.join(logs_folder, og_file))
                        except Exception as e:
                            print(f"Error deserializing original points: {e}")
                            og_right_points, og_left_points = None, None  # Reset in case of error

                plot_trajectory_and_cones(mid_points, right_points, left_points, og_right_points, og_left_points, plot_initial_box_flag)
                plot_initial_box_flag = False
                time.sleep(1.5)

            except Exception as e:
                print(f"An error occurred during plotting: {e}")


    except FileNotFoundError:
        print(f"Logs folder not found: {logs_folder}")
    except Exception as e:
        print(f"An error occurred: {e}")




if __name__ == "__main__":
    plotter("logs")



