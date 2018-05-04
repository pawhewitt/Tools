""" Plots the first conservative, CL and Cd residual value""" 

import numpy as np
import matplotlib.pyplot as plt
from optparse import OptionParser

def main():

	parser=OptionParser()
	parser.add_option("-f",dest="file",help="history file",default="history.vtk")
	(options,args)=parser.parse_args()
	file=options.file
	# Read File
	hist=np.loadtxt(file,skiprows=1,delimiter=',')
	# tranpose data
	hist=np.transpose(hist)
	
	# Plot the data
	# Cl convergence 
	plt.plot(hist[0],hist[1],label="Cl")
	# Cd convergence
	plt.plot(hist[0],hist[1],label="Cd")
	# Conservative 1
	plt.plot(hist[0],hist[13],label="Res[0]")

	# Show the graph
	plt.legend()
	plt.grid()
	plt.show()



if __name__=="__main__":
	main()