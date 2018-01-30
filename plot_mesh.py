# Plot surface marker from one or two mesh files

import sys,os
sys.path.append(os.environ['SU2_RUN'])
import SU2 # import all the python scripts in /usr/local/SU2_RUN/SU2_PY/SU2
import numpy as np
import matplotlib.pyplot as plt
from optparse import OptionParser

parser=OptionParser()
parser.add_option("-a",dest="mesh_a", help="Name of the First Mesh")
parser.add_option("-b",dest="mesh_b", help="Name of the Second Mesh",default="NULL")

def Main():

	marker=raw_input("Marker name = ")
	save=raw_input("Save Figure? (y/n)")

	(options,args)=parser.parse_args()
	a=options.mesh_a
	b=options.mesh_b

	# Plot First Mesh
	Coords_a=Read_Mesh(a,marker)
	Plot_Mesh(a,Coords_a)

	# Plot Second mesh if provided
	if b!="NULL":
		Coords_b=Read_Mesh(b,marker)
		Plot_Mesh(b,Coords_b)

	if save=="y": 
		plt.savefig('Marker_Geometry.png',dpi=150)
	
	plt.grid()
	plt.show()	
	plt.close()

def Read_Mesh(a,marker):
	# Get the mesh data
	Meshdata=SU2.mesh.tools.read(a)
	# Extract the marker geometry
	Points,Loop=SU2.mesh.tools.sort_airfoil(Meshdata,marker)
	# Reorder in an anticlockwise direction from trailing edge
	Foil_Points,Foil_Nodes=SU2.mesh.tools.get_markerPoints(Meshdata,marker)
	Coords=np.zeros([len(Points),2])
	for i in range(len(Points)):
		Coords[i][0]=Foil_Points[Loop[i]][0]
		Coords[i][1]=Foil_Points[Loop[i]][1]

	return Coords

def Plot_Mesh(Design,Coords):
	Coords=np.transpose(Coords)
	plt.plot(Coords[0],Coords[1],label="Design "+Design)
	plt.legend()
	plt.title('Marker Geometry')

	return

if __name__=="__main__":
	Main()