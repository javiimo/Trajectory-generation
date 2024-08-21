# Trajectory Generator

This repository contains Python scripts for generating and visualizing trajectories based on cone positions.

## Files

* **`point_gen.py`**: This script generates cone coordinates for different track layouts, including curves and straight sections with slaloms. It can save these coordinates to a file for use with `clean_trajectory_generator.py`.

* **`clean_trajectory_generator.py`**: This script computes a vehicle trajectory based on detected cone positions. It reads cone coordinates from a file, processes them, adds some complexity like disordering the cones and randomly removing some cones and generates a robust path. This is the working version.

* **`draft_trajectory_generator.py`**: This file contains earlier, less refined versions of the trajectory generation algorithm. It's kept for reference and experimentation and contains other approaches that do not work in all the tested cases.

## Usage

1. **Generate Cone Positions:** Use `point_gen.py` to create a file containing cone coordinates. You can customize the track layout parameters within the script. `map.dat` and `circ_map.dat` where created using this script.

2. **Compute Trajectory:** Run `clean_trajectory_generator.py` and provide the name of the file containing the cone coordinates. The script will generate and visualize the trajectory step by step.

## Note

The scripts rely on accurate cone detection and differentiation between left and right cones. Incorrect identification will lead to inaccurate trajectories.