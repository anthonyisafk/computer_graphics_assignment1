from util import *

if __name__ == "__main__":
	data = np.load("hw1.npy", allow_pickle=True)[()] # initialize as dictionary.
	verts2d = data['verts2d']
	vcolors = data['vcolors']
	faces = data['faces']
	depth = data['depth']

	img = render(verts2d, faces, vcolors, depth, "flat", show=True)

	cv.imshow("Flat coloring test", img)
	cv.waitKey(0)
	cv.destroyAllWindows()



