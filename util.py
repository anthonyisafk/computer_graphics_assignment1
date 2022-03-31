import cv2 as cv
from color import *
from helpers import *
import numpy as np


def render(verts2d, faces, vcolors, depth, shade_t, M=512, N=512, refresh=False):
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
	sorted_triangle_depth_idx = np.argsort(triangle_depth)[::-1] # sort in descending order

	if not refresh:
		for idx in sorted_triangle_depth_idx:
			img = shade_triangle(img, verts2d[faces[idx]], vcolors[faces[idx]], shade_t)
		cv.imshow(f"Rendered image with shade_t = {shade_t}", img)
		cv.waitKey(0)
		cv.destroyAllWindows()
	else:
		for idx in sorted_triangle_depth_idx:
			img = shade_triangle(img, verts2d[faces[idx]], vcolors[faces[idx]], shade_t)
			cv.imshow(f"Rendering image with shade_t = {shade_t}", img)
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
	has_horizontal_edges = np.count_nonzero(mi) != 3 # check for horizontal edge

	img, active_edges, active_points, horizontal_edge_first = flat_handle_first_edge(
		img, ykmin, ymin, xkmin, xkmax, mi, bi, has_horizontal_edges, flat_color
	)

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


