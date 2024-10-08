from utility_funcs import *
import time
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation



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
    Constantly monitors the logs folder for new files and plots the latest data.
    """
    plot_initial_box_flag = True # Flag to plot initial box only in the first iteration

    while True: # Loop indefinitely
        latest_seen_points_time = 0
        latest_midpoints_time = 0
        latest_og_points_time = 0

        right_points, left_points, mid_points, og_right_points, og_left_points = None, None, None, None, None # Initialize to None

        try:
            files = os.listdir(logs_folder)

            # Find latest files for each category based on timestamp in filename
            for file in files:
                try:
                    if "_" in file: # Check if filename contains "_"
                        name, timestamp_str = file.split("_", 1)  # Split into name and timestamp
                        if "." in timestamp_str:
                            timestamp_str = timestamp_str.split(".")[0] #remove extension if present
                        timestamp = int(timestamp_str)
                    else:
                        print(f"Skipping invalid filename format: {file}")
                        continue

                    if "seenpoints" in name:
                        if timestamp > latest_seen_points_time:
                            latest_seen_points_time = timestamp
                            latest_seen_points_file = os.path.join(logs_folder, file)
                    elif "midpoints" in name:
                        if timestamp > latest_midpoints_time:
                            latest_midpoints_time = timestamp
                            latest_midpoints_file = os.path.join(logs_folder, file)
                    elif "ogpoints" in name:
                        if timestamp > latest_og_points_time:
                            latest_og_points_time = timestamp
                            latest_og_points_file = os.path.join(logs_folder, file)


                except ValueError: # Handle files without timestamps or other formats
                    print(f"Skipping invalid filename format: {file}")
                    continue

            # Deserialize data, handling potential errors
            if latest_seen_points_time > 0:
                try:
                    right_points, left_points = deserialize_points(latest_seen_points_file)
                except Exception as e:
                    print(f"Error deserializing seen points: {e}")
            if latest_midpoints_time > 0:
                try:
                    mid_points = deserialize_midpoints(latest_midpoints_file)
                except Exception as e:
                    print(f"Error deserializing mid points: {e}")
            if latest_og_points_time > 0:
                try:
                    og_right_points, og_left_points = deserialize_points(latest_og_points_file)
                except Exception as e:
                    print(f"Error deserializing original points: {e}")

            # Plot even if only some data is available
            plot_trajectory_and_cones(mid_points, right_points, left_points, og_right_points, og_left_points, plot_initial_box_flag) # Pass the flag to the plotting function
            plot_initial_box_flag = False # Set flag to False after the first iteration

        except FileNotFoundError:
            print(f"Logs folder not found: {logs_folder}")
        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(5) # Wait 5 seconds before the next check



if __name__ == "__main__":
    plotter("logs")



