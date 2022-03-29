from typing import Tuple
import numpy as np


def find_edges(verts2d) -> \
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
	mi = np.empty((3), dtype=np.float32)
	bi = np.empty((3), dtype=np.float32)

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


def find_intersecting_points(active_edges, xkmin, mi, bi, y):
	"""Finds the intersecting points of a scanline and the active edges

	:param xkmin: Used in case m == \infty
	:param y: The y coordinate of the scanline

	:returns: The lower and upper bound of the continuous filling interval
	"""
	intersect_points = np.empty((2), dtype=np.int)
	for i in range(2):
		m_i = mi[int(active_edges[i])]
		b_i = bi[int(active_edges[i])]
		if m_i == float("inf"):
			intersect_points[i] = xkmin[int(active_edges[i])]
		else:  # if m == 0 we don't need to change the active points
			intersect_points[i] = round((y + 1 - b_i) / m_i)

	return np.sort(intersect_points)