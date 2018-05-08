# script to plot the geometry contained in the Initial_Design.txt file

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

def main():

	coords=np.loadtxt('mesh_motion.dat') # Get coords from File
	fig=plt.figure() # Create figure object
	geom=fig.add_subplot(111,projection='3d')

	# shape=np.shape(coords)

	# print coords[:,1:3]


	coords=np.transpose(coords) # transpose coords for plotting

	
	print len(coords)	

	if len(coords)==3:
		geom.scatter(coords[1],coords[2]) 
		plt.xlabel('x')
		plt.ylabel('y')
		
	else:
		geom.scatter(coords[1],coords[2],coords[3]) 
		plt.xlabel('x')
		plt.ylabel('y')
	plt.show()


if __name__ == '__main__':
    main()