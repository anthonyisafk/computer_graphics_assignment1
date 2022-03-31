from typing import Tuple
import numpy as np
import math


def find_edges(verts2d: np.ndarray) -> \
	Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
	"""
	| Edge #i is described by:
	| xkmin[i]-xkmax[i]
	| ykmin[i]-ykmax[i]
	| mi[i] and bi[i] (as in y = m*x + b)
	"""
	xkmax = np.empty((3), dtype=np.int)
	xkmin = np.empty((3), dtype=np.int)
	ykmax = np.empty((3), dtype=np.int)
	ykmin = np.empty((3), dtype=np.int)
	mi = np.empty((3))
	bi = np.empty((3))

	for i in range(3):
		# Use `(i + 1) % 3` to account for the last iteration going out of bounds.
		xstart = verts2d[i][1]
		xend = verts2d[(i + 1) % 3][1]
		ystart = verts2d[i][0]
		yend = verts2d[(i + 1) % 3][0]

		if xstart >= xend:
			xkmax[i] = xstart
			xkmin[i] = xend
		else:
			xkmax[i] = xend
			xkmin[i] = xstart
		if ystart >= yend:
			ykmax[i] = ystart
			ykmin[i] = yend
		else:
			ykmax[i] = yend
			ykmin[i] = ystart

		if xstart == xend:
			mi[i] = float("inf")
			bi[i] = 0
		else:
			mi[i] = (ystart - yend) / (xstart - xend)
			bi[i] = ystart - mi[i] * xstart

	return xkmin, xkmax, ykmin, ykmax, mi, bi


def find_intersecting_points(active_edges, xkmin, mi, bi, y) -> np.ndarray:
	"""Finds the intersecting points of a scanline and the active edges

	:param xkmin: Used in case m == \infty
	:param y: The y coordinate of the scanline

	:returns: The lower and upper bound of the continuous filling interval
	"""
	intersect_points = np.empty((2), dtype=np.float32)
	integer_values = np.empty((2), dtype=np.int)
	for i in range(2):
		m_i = mi[int(active_edges[i])]
		b_i = bi[int(active_edges[i])]
		if m_i == float("inf") or m_i == 0:
			intersect_points[i] = xkmin[int(active_edges[i])]
		else:  # if m == 0 we don't need to change the active points
			intersect_points[i] = (y - b_i) / m_i

	# Check if the point is at the rightmost or leftmost part - process accordingly.
	if intersect_points[0] > intersect_points[1]:
		integer_values[0] = math.floor(intersect_points[1])
		integer_values[1] = math.ceil(intersect_points[0])
	else:
		integer_values[0] = math.floor(intersect_points[0])
		integer_values[1] = math.ceil(intersect_points[1])

	del intersect_points
	return integer_values


def flat_handle_first_edge(
	img, ykmin, ymin, xkmin, xkmax, mi, bi,
	has_horizontal_edges, flat_color
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, bool]:
	horizontal_edge_first = False
	active_edges = np.array([])
	active_points = np.empty((2), dtype=np.int) # use this as [start, end] since the points are always contiguous
	if has_horizontal_edges:
		for i in range(3):
			if mi[i] == 0: # check if the first edge is horizontal
				if ykmin[i] == ymin:
					horizontal_edge_first = True
					active_points = np.sort(np.array([xkmin[i], xkmax[i]]))
					active_edges = np.arange(3)
					active_edges = active_edges[active_edges != i] # exclude the current edge from the active ones.
					break
				else:
					for i in range(3):
						if ykmin[i] == ymin:
							active_edges = np.append(active_edges, i)
					active_points = find_intersecting_points(active_edges, xkmin, mi, bi, ymin + 1)
		if horizontal_edge_first:
			for point in range(active_points[0], active_points[1]):
				img[ymin][point] = flat_color
	else:
		for i in range(3):
			if ykmin[i] == ymin:
				active_edges = np.append(active_edges, i)
		active_points = find_intersecting_points(active_edges, xkmin, mi, bi, ymin + 1)

	return img, active_edges, active_points, horizontal_edge_first