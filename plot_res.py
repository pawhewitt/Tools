""" Plots the first conservative, CL and Cd residual value""" 

import numpy as np
import matplotlib.pyplot as plt

def main():
	# Read File
	hist=np.loadtxt('history.vtk',skiprows=1,delimiter=',')
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