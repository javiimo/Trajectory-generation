import unittest
from utility_funcs import *


def merge_too_close_points(mid_points, dist_tol=3.1):
    """Merges points in a list that are closer than a given distance tolerance. But does not merge more than 2 consecutive points.
    Does a second pass of merging so that it merges up to 3 or 4 consecutive points if they are very very close to each other

    Args:
        mid_points: A list of points, where each point is a list of coordinates [x, y].
        dist_tol: The distance tolerance below which points are merged.

    Returns:
        A new list of points with close points merged.
    """
    if not mid_points:  # Handle empty list case
        return []

    if len(mid_points) == 1:
        return mid_points
    
    merged_points =[]
    i = 0
    while i < len(mid_points) -1:
        if euclidean_norm(mid_points[i], mid_points[i+1]) <= dist_tol:
            merged_points.append(compute_midpoint(mid_points[i], mid_points[i + 1]))
            i +=2 # Skip the next point since it was already merged
        else:
            merged_points.append(mid_points[i])
            i += 1

    if i == len(mid_points) -1: # Add the last point if it wasn't merged
        merged_points.append(mid_points[i])

    i = 0
    merged_points2 = []
    while i < len(merged_points) - 1:
        if euclidean_norm(merged_points[i], merged_points[i+1]) <= dist_tol/2:
            merged_points2.append(compute_midpoint(merged_points[i], merged_points[i + 1]))
            i += 2
        else:
            merged_points2.append(merged_points[i])
            i += 1
    if i == len(merged_points) - 1:
        merged_points2.append(merged_points[i])


    return merged_points2


class TestMergeTooClosePoints(unittest.TestCase):

    def test_empty_list(self):
        self.assertEqual(merge_too_close_points([]), [])

    def test_single_point(self):
        self.assertEqual(merge_too_close_points([[1, 2]]), [[1, 2]])

    def test_two_close_points(self):
        points = [[1, 2], [1.1, 2.2]]
        merged_points = merge_too_close_points(points)
        self.assertEqual(len(merged_points), 1)
        self.assertAlmostEqual(merged_points[0][0], 1.05)
        self.assertAlmostEqual(merged_points[0][1], 2.1)
    
    def test_two_distant_points(self):
        points = [[1,2], [4,5]]
        merged_points = merge_too_close_points(points)
        self.assertEqual(len(merged_points), 2)
        self.assertEqual(merged_points, [[1,2], [4,5]])

    def test_three_close_points(self):
        points = [[1, 2], [1.1, 2.1], [1.2, 2.2]]
        merged_points = merge_too_close_points(points)
        self.assertEqual(len(merged_points), 1)
        self.assertAlmostEqual(merged_points[0][0], 1.1)
        self.assertAlmostEqual(merged_points[0][1], 2.1)

    def test_several_points(self):
        points = [[1,1], [1.1, 1.1], [2,3], [2.1, 3.1], [4,5], [7,7], [7.2, 7.2]]
        merged_points = merge_too_close_points(points, dist_tol=0.3)
        self.assertEqual(len(merged_points), 4)
        self.assertAlmostEqual(merged_points[0][0], 1.05)
        self.assertAlmostEqual(merged_points[0][1], 1.05)
        self.assertAlmostEqual(merged_points[1][0], 2.05)
        self.assertAlmostEqual(merged_points[1][1], 3.05)
        self.assertEqual(merged_points[2], [4,5])
        self.assertAlmostEqual(merged_points[3][0], 7.1)
        self.assertAlmostEqual(merged_points[3][1], 7.1)

    def test_alternating_close_and_distant(self):
        points = [[1, 2], [1.1, 2.1], [3, 4], [5, 6], [5.1, 6.1]]
        merged_points = merge_too_close_points(points)
        self.assertEqual(len(merged_points), 3)
        self.assertAlmostEqual(merged_points[0][0], 1.05)
        self.assertAlmostEqual(merged_points[0][1], 2.1)
        self.assertEqual(merged_points[1], [3, 4])
        self.assertAlmostEqual(merged_points[2][0], 5.05)
        self.assertAlmostEqual(merged_points[2][1], 6.05)

if __name__ == '__main__':
    unittest.main()
