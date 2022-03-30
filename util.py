import cv2 as cv
from color import *
from helpers import *
import numpy as np


def render(verts2d, faces, vcolors, depth, shade_t, M=512, N=512, show=False):
	if shade_t != "flat" and shade_t != "gouraud":
		raise Exception("\"shade_t\" can either be \"flat\" or \"gouraud\"!")

	for i in range(len(vcolors)):
		vcolors[i] = np.flip(vcolors[i])

	img = np.ones((M, N, 3))
	for i in range(len(verts2d)):
		img[int(verts2d[i, 0])][int(verts2d[i, 1])] = vcolors[i]

	triangles_num = len(faces)
	triangle_depth = np.empty((triangles_num))
	for i in range(triangles_num):
		triangle_depth[i] = np.mean(depth[faces[i]])
	sorted_triangle_depth_idx = np.argsort(triangle_depth)[::-1]

	if not show:
		for idx in sorted_triangle_depth_idx:
			img = shade_triangle(img, verts2d[faces[idx]], vcolors[faces[idx]], shade_t)
	else:
		for idx in sorted_triangle_depth_idx:
			img = shade_triangle(img, verts2d[faces[idx]], vcolors[faces[idx]], shade_t)
			cv.imshow(f"Render - shade_t = {shade_t}", img)
			cv.waitKey(1)

	return img


def shade_triangle(img, verts2d, vcolors, shade_t):
	if shade_t != "flat" and shade_t != "gouraud":
		raise Exception("\"shade_t\" can either be \"flat\" or \"gouraud\"!")

	xkmin, xkmax, ykmin, ykmax, mi, bi = find_edges(verts2d)

	if shade_t == "flat":
		flat_color = get_flat_color(vcolors)
		img = shade_triangle_flat(img, ykmin, ykmax, xkmin, xkmax, mi, bi, flat_color)
	else:
		img = shade_triangle_gouraud(img, ykmin, ykmax, xkmin, xkmax, mi, bi, vcolors)

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

	for y in range(ymin, ymax):
		for point in range(active_points[0], active_points[1]):
			img[y][point] = flat_color
		for i in range(2): # check for new edges, this means an old one will be replaced
			if ykmax[int(active_edges[i])] == y:
				replace = np.arange(3)
				active_edges = replace[replace != active_edges[i]]
				del replace
		active_points = find_intersecting_points(active_edges, xkmin, mi, bi, y + 1)

	return img


def shade_triangle_gouraud(img, ykmin, ykmax, xkmin, xkmax, mi, bi, vcolors):
	pass

