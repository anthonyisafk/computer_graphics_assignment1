import numpy as np


def interpolate_color(x1, x2, x, C1, C2) -> np.ndarray:
	"""Use linear interpolation over one dimension to determine a point's color

	:param x1: The respective coordinate of triangle vertex V1
	:param x2: The respective coordinate of triangle vertex V2
	:param x: The respective coordinate of the point whose color the function determines
	:param C1: The RGB values of vertex V1
	:param C2: The RGB values of vertex V2

	:returns: The RGB values of point x
	"""
	if x2 == x1:
		raise Exception("x2 == x1: Cannot divide by zero!")
	value = np.empty((3), dtype=np.float32)
	interp_coeffs = np.empty((2), dtype=np.float32)

	# No need to check for sign. The two operands cancel each other out in case of negativity.
	# This happens because x is supposed to be between x1 and x2.
	interp_coeffs[0] = (x - x1) / (x2 - x1)
	interp_coeffs[1] = 1 - interp_coeffs[0]
	for i in range(3):
		value[i] = interp_coeffs[0] * C1[i] + interp_coeffs[1] * C2[i]

	return value


def get_flat_color(vcolors):
	"""Calculates the unweighted mean of the RGB values from a set of vertices."""
	n = len(vcolors)
	color = np.empty((3), dtype=np.float32)
	for i in range(n):
		for j in range(3):
			color[j] += vcolors[i][j]
	color = [color[i] / n for i in range(3)]

	return color