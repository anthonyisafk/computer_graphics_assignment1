import numpy as np
import cv2 as cv
from color import *
from util import *

if __name__ == "__main__":
	start = 2
	end = 5
	M = 512
	N = 512

	data = np.load("hw1.npy", allow_pickle=True)[()] # initialize as dictionary.
	verts2d = data['verts2d']
	vcolors = data['vcolors']
	faces = data['faces']
	depth = data['depth']

	for i in range(len(vcolors)):
		vcolors[i] = vcolors[i][[2, 1, 0]]

	img = np.ones((M, N, 3))
	for i in range(len(verts2d)):
		img[int(verts2d[i, 0])][int(verts2d[i, 1])] = vcolors[i]

	triangles_num = len(faces)
	triangle_depth = np.empty((triangles_num))
	for i in range(triangles_num):
		triangle_depth[i] = np.min(depth[faces[i]])
	sorted_triangle_depth_idx = np.argsort(triangle_depth)

	for idx in sorted_triangle_depth_idx:
		img = shade_triangle(img, verts2d[faces[idx]], vcolors[faces[idx]], "flat")
		# cv.imshow("Flat coloring test", img)
		# cv.waitKey(1)

	cv.imshow("Flat coloring test", img)
	cv.waitKey(0)
	cv.destroyAllWindows()



