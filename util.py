from typing import Tuple
from color import *
from helpers import *
import numpy as np


def shade_triangle(img, verts2d, vcolors, shade_t):
	if shade_t != "flat" and shade_t != "gouraud":
		raise Exception("\"shade_t\" can either be \"flat\" or \"gouraud\"!")

	xkmin, xkmax, ykmin, ykmax, mi, bi = find_edges(verts2d)

	if shade_t == "flat":
		flat_color = get_flat_color(vcolors)
		img = shade_triangle_flat(img, ykmin, ykmax, xkmin, xkmax, mi, bi, flat_color)

	return img


def shade_triangle_flat(img, ykmin, ykmax, xkmin, xkmax, mi, bi, flat_color):
	# Every triangle is convex. This means ymin will either give us 2 active edges or
	# one edge (which we will not add to the active ones, since it will be horizontal).
	# Find the active points of the second iteration either way.
	ymin = min(ykmin)
	ymax = max(ykmax)
	active_edges = np.array([])
	active_points = np.empty((2), dtype=np.int) # use this as [start, end] since the points are always contiguous
	has_horizontal_edges = np.count_nonzero(mi) != 3 # check for horizontal edge
	horizontal_edge_first = False # keep track if the horizontal edge is first or last

	if has_horizontal_edges: # check if the first edge is horizontal
		for i in range(3):
			if mi[i] == 0:
				if ykmin[i] == ymin:
					horizontal_edge_first = True
					active_points = np.sort(np.array([xkmin[i] + 1, xkmax[i] - 1]))
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

	# Done with the first iteration. If the horizontal edge was the first one, iterate through ymax.
	# Otherwise follow the algorithm until ymax - 1 and fill the horizontal edge separately.
	yend = ymax if horizontal_edge_first else ymax - 1
	for y in range(ymin + 1, yend):
		for point in range(active_points[0], active_points[1]):
			img[y][point] = flat_color
		for i in range(2): # check for new edges, this means an old one will be replaced
			if ykmax[int(active_edges[i])] == y:
				replace = np.arange(3)
				active_edges = replace[replace != active_edges[i]]
				del replace
		active_points = find_intersecting_points(active_edges, xkmin, mi, bi, y + 1)

	if not horizontal_edge_first:
		for i in range(3):
			if mi[i] == 0:
				active_points = np.sort(np.array([xkmin[i] + 1, xkmax[i] - 1]))
				break
		for point in range(active_points[0], active_points[1]):
			img[ymax][point] = flat_color

	return img


def shade_triangle_gouraud(img, verts2d, vcolors):
	pass

