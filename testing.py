from util import *

if __name__ == "__main__":
	data = np.load("hw1.npy", allow_pickle=True)[()] # initialize as dictionary.
	verts2d = data['verts2d']
	vcolors = data['vcolors']
	faces = data['faces']
	depth = data['depth']

	img = render(verts2d, faces, vcolors, depth, "gouraud", refresh=False)

	# img = img * 255
	# cv.imwrite("flat.jpg", img)



