from typing import Tuple
from color import interpolate_color
import numpy as np
import math

def find_edges(verts2d: np.ndarray) -> \
	Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray,
		  np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
	"""
	| Edge #i consists of vertices i and i+1 and is described by:
	| xkmin[i]-xkmax[i]
	| ykmin[i]-ykmax[i]
	| mi[i] and bi[i] (as in y = m*x + b)
	"""
	xkmax = np.empty((3), dtype=np.int)
	xkmin = np.empty((3), dtype=np.int)
	ykmax = np.empty((3), dtype=np.int)
	ykmin = np.empty((3), dtype=np.int)
	mi = np.empty((3), dtype=np.float16)
	bi = np.empty((3), dtype=np.float16)
	# Keep who owns the minimum and maximum y([0]) and x([1]) values
	min_owners = np.empty((3, 2), dtype=np.int)
	max_owners = np.empty((3, 2), dtype=np.int)

	for i in range(3):
		# Use `(i + 1) % 3` to account for the last iteration going out of bounds.
		next_vertex = (i + 1) % 3
		xstart = verts2d[i][1]
		xend = verts2d[next_vertex][1]
		ystart = verts2d[i][0]
		yend = verts2d[next_vertex][0]

		if xstart >= xend:
			xkmax[i] = xstart
			xkmin[i] = xend
			max_owners[i, 1] = i
			min_owners[i, 1] = next_vertex
		else:
			xkmax[i] = xend
			xkmin[i] = xstart
			max_owners[i, 1] = next_vertex
			min_owners[i, 1] = i
		if ystart >= yend:
			ykmax[i] = ystart
			ykmin[i] = yend
			max_owners[i, 0] = i
			min_owners[i, 0] = next_vertex
		else:
			ykmax[i] = yend
			ykmin[i] = ystart
			max_owners[i, 0] = next_vertex
			min_owners[i, 0] = i

		if xstart == xend:
			mi[i] = float("inf")
			bi[i] = 0
		else:
			# Keep in mind: y = mx + b => b = y - mx
			mi[i] = (ystart - yend) / (xstart - xend)
			# We have to make a calculation that is as precise as possible,
			# so we use both of the equations we have available.
			bi[i] = np.mean([ystart - mi[i] * xstart, yend - mi[i] * xend])

	return xkmin, xkmax, ykmin, ykmax, max_owners, min_owners, mi, bi


def find_intersecting_points(active_edges, xkmin, xkmax, mi, bi, y):
	"""Finds the intersecting points of a scanline and the active edges

	:returns: The lower and upper bound of the continuous filling interval
	"""
	intersect_points = np.empty((2), dtype=np.int)
	for i in range(2):
		active_edge = active_edges[i]
		m_i = mi[active_edge]
		b_i = bi[active_edge]
		if m_i == float("inf"):
			intersect_points[i] = xkmin[active_edge]
		elif m_i == 0:
			intersect_points = np.array([xkmin[active_edge], xkmax[active_edge]])
			break
		else:
			intersect_points[i] = np.round((y - b_i) / m_i)

	return np.sort(intersect_points)
	# return intersect_points
	# return np.array([math.floor(intersect_points[0]), math.ceil(intersect_points[1])])


def flat_handle_first_edge(
	img, verts2d, ykmin, ykmax, ymin, xkmin, xkmax, first_edge_horizontal
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
	active_edges = np.array([], dtype=np.int)
	active_points = np.empty((2), dtype=np.int) # use this as [start, end] since the points are always contiguous
	if first_edge_horizontal:
		for i in range(3):
			if ykmin[i] == ykmax[i]: # check if the first edge is horizontal
				active_points = np.sort(np.array([xkmin[i], xkmax[i]]))
				active_edges = np.arange(3)
				active_edges = active_edges[active_edges != i] # exclude the current edge from the active ones.
				break
	else:
		for i in range(3):
			if ykmin[i] == ymin:
				active_edges = np.append(active_edges, i)
		active_edges = active_edges[np.argsort(xkmin[active_edges])]
		vertex = int(verts2d[active_edges[0]][1])
		active_points = np.array([vertex, vertex])

	return img, active_edges, active_points


def gouraud_handle_first_edge(
	img, verts2d, ykmin, ykmax, ymin, xkmin, xkmax, mi, bi, min_owners, first_edge_horizontal
):
	active_edges = np.array([], dtype=np.int)
	active_points = np.empty((2), dtype=np.int) # use this as [start, end] since the points are always contiguous
	if first_edge_horizontal:
		for i in range(3):
			if ykmin[i] == ykmax[i]:
				active_points = np.array([xkmin[i], xkmax[i]])
				active_edges = np.arange(3)
				active_edges = active_edges[active_edges != i] # exclude the current edge from the active ones.
				break
	else:
		for i in range(3):
			if ykmin[i] == ymin:
				active_edges = np.append(active_edges, i)
		active_edges = active_edges[np.argsort(xkmin[active_edges])]
		active_points = find_intersecting_points(active_edges, xkmin, xkmax, mi, bi, ymin)

	order = np.argsort(xkmin[active_edges])
	return img, active_edges[order], np.sort(active_points)


def gouraud_outline_and_interpolate(
	img, vcolors, active_edges, active_points, min_owners, max_owners,
	ykmin, ykmax, xkmin, xkmax, ymin, ymax, mi, bi
):
	all = np.arange(3)
	for y in range(ymin, ymax + 1):
		# if False:
		if np.any(mi[active_edges] == 0):
			# print("Found horizontal edge in gouraud_outline_and_interpolate()")
			pass
		else:
			for i in range(2):
				p = active_edges[i]
				ymin_p = ykmin[p]
				ymax_p = ykmax[p]
				C1 = vcolors[min_owners[p, 0]]
				C2 = vcolors[max_owners[p, 0]]
				img[y][active_points[i]] = interpolate_color(ymin_p, ymax_p, y, C1, C2)

		C1 = img[y][active_points[0]]
		C2 = img[y][active_points[1]]
		for p in range(active_points[0] + 1, active_points[1]):
			img[y][p] = interpolate_color(active_points[0], active_points[1], p, C1, C2)

		extra_edge = np.delete(all, active_edges) # keep the edge that is not active
		for i in range(2): # check for new edges, this means an old one will be replaced
			if ykmax[int(active_edges[i])] == y:
				active_edges[i] = extra_edge
		active_points = find_intersecting_points(active_edges, xkmin, xkmax, mi, bi, y + 1)

	return img
