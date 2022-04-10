"""
@author: Antonios Antoniou
@email: aantonii@ece.auth.gr
******************************
@brief: Demo showcasing the flat color shading algorithm.
@instructions: Set `refresh=True` if you want to see a sneak peek of the
			   resulting picture during the execution of the algorithm.
******************************
2022 Aristotle University Thessaloniki - Computer Graphics
"""
from util import *

if __name__ == "__main__":
	data = np.load("hw1.npy", allow_pickle=True)[()] # initialize as dictionary.
	verts2d = data['verts2d']
	vcolors = data['vcolors']
	faces = data['faces']
	depth = data['depth']

	img = render(verts2d, faces, vcolors, depth, "flat", refresh=False)

	img = img * 255
	cv.imwrite("flat.jpg", img)