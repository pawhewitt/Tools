# De-bugging Script to compare the geometries of the fitted CST
# foil from the python scripts and the mesh produced by SU2_DEF


import sys,os
sys.path.append(os.environ['SU2_RUN'])
import SU2 # import all the python scripts in /usr/local/SU2_RUN/SU2_PY/SU2
import numpy as np
import matplotlib.pyplot as plt


def main():

	CST=np.loadtxt("CST_Coords.dat")

	marker="airfoil" # or AIRFOIL for RAE
	# Using the Su2 python scripts for reading mesh
	Meshdata=SU2.mesh.tools.read("mesh_out.su2") # read the mesh

	# sort airfoil coords to be arrange clockwise from trailing edge
	Points,Loop=SU2.mesh.tools.sort_airfoil(Meshdata,marker)
	
	# get the points for the surface marker
	Foil_Points,Foil_Nodes=SU2.mesh.tools.get_markerPoints(Meshdata,marker)

	#Get the sorted points 
	DEF=np.zeros([len(Points),2])
	for i in range(len(Points)):
		DEF[i][0]=Foil_Points[Loop[i]][0]
		DEF[i][1]=Foil_Points[Loop[i]][1]
	
	CST=np.transpose(CST)
	DEF=np.transpose(DEF)
	plt.plot(CST[0],CST[1],label='CST')
	plt.plot(DEF[0],DEF[1],label='SU2_DEF')
	plt.legend()
	plt.grid()
	plt.show()


if __name__=='__main__':
	main()	