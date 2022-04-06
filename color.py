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
		return C1
	value = np.empty((3))
	for i in range(3):
		value[i] = np.interp(x, [x1, x2], [C1[i], C2[i]])

	return value


def get_flat_color(vcolors: np.ndarray) -> np.ndarray:
	"""Calculates the unweighted mean of the RGB values from a set of vertices."""
	color = np.mean(vcolors, axis=0)
	return color