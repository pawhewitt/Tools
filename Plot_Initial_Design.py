# script to plot the geometry contained in the Initial_Design.txt file

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

def main():

	coords=np.loadtxt('/home/phewitt/Dropbox/Opt_Sync/Initial_Design.txt') # Get coords from File
	fig=plt.figure() # Create figure object
	geom=fig.add_subplot(111,projection='3d')

	coords=np.transpose(coords) # transpose coords for plotting

	if len(coords)==2:
		geom.scatter(coords[0],coords[1]) 
	
	else:
		geom.scatter(coords[0],coords[1],coords[2]) 

	plt.xlabel('x')
	plt.ylabel('y')
	plt.show()


if __name__ == '__main__':
    main()