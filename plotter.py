from utility_funcs import *
import time
import os
import matplotlib.pyplot as plt
import time
import cv2
import os
import shutil


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
    if right_points:
        x, y = zip(*right_points)
        ax.scatter(x, y, c='y', label='Detected right cones')
    if left_points:
        x, y = zip(*left_points)
        ax.scatter(x, y, c='b', label='Detected left cones')

    # Plot undetected cones if available
    if og_right_points and og_left_points: # Only plot undetected if original points are available
        all_detected = right_points + left_points
        undetected = [p for p in og_right_points + og_left_points if all_detected is None or p not in all_detected]
        if undetected:
            x, y = zip(*undetected)
            ax.scatter(x, y, c='r', label='Undetected cones')

    ax.legend()
    ax.axis('equal')

    plt.draw() # Draw the plot
    plt.pause(0.001) # Pause to allow the plot to update


def plotter(logs_folder="logs", video=False):
    """
    Plots data from files in the logs folder, matching timestamps between midpoints, seenpoints, and ogpoints.
    If video is True, saves plots to a temporary folder and creates a video.
    """
    plot_initial_box_flag = True
    temporal_folder = "temporal"  # Folder to store temporary images for video

    try:
        if video:
            os.makedirs(temporal_folder, exist_ok=True)

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

                if video:
                    plt.savefig(os.path.join(temporal_folder, f"frame_{i:04d}.png"))
                else:
                    #time.sleep(1.5)
                    plt.waitforbuttonpress()

            except Exception as e:
                print(f"An error occurred during plotting: {e}")

        if video:
            create_video_from_images(temporal_folder, "output.mp4")  # Create video
            shutil.rmtree(temporal_folder)  # Remove temporary folder

    except FileNotFoundError:
        print(f"Logs folder not found: {logs_folder}")
    except Exception as e:
        print(f"An error occurred: {e}")




def create_video_from_images(image_folder, output_video_path, fps=1):
    """Creates a video from a sequence of images in a folder.

    Args:
        image_folder: Path to the folder containing the image sequence.
        output_video_path: Path to the output video file.
        fps: Frames per second for the output video.
    """
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    images.sort()  # Ensure images are in correct order

    if not images:
        print("No images found in the specified folder.")
        return

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use mp4v codec
    video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()



if __name__ == "__main__":
    plotter("logs", video=True)



