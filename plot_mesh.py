# Plot surface marker from one or two mesh files

import sys,os
sys.path.append(os.environ['SU2_RUN'])
import SU2 # import all the python scripts in /usr/local/SU2_RUN/SU2_PY/SU2
import numpy as np
import matplotlib.pyplot as plt
from optparse import OptionParser
# For 3D plots
from mpl_toolkits.mplot3d import Axes3D

parser=OptionParser()
parser.add_option("-a",dest="mesh_a", help="Name of the First Mesh",default="NULL")
parser.add_option("-b",dest="mesh_b", help="Name of the Second Mesh",default="NULL")

def Main():

	marker=raw_input("Marker name = ")
	save=raw_input("Save Figure? (y/n)")
	dim= raw_input("2D or 3D?")

	# marker='wing'
	# save="n"
	# dim= "3D"

	(options,args)=parser.parse_args()
	a=options.mesh_a
	b=options.mesh_b

	if a=="NULL":
		print "provide file name with -a agrument"

	fig=plt.figure()
	if dim=="3D":
		geom=fig.add_subplot(111,projection="3d")
	else:
		geom="NULL"

	# Plot First Mesh
	Coords_a=Read_Mesh(a,marker,dim)
	Plot_Mesh(a,Coords_a,dim,geom,'a')

	# Plot Second mesh if provided
	if b!="NULL":
		Coords_b=Read_Mesh(b,marker,dim)
		Plot_Mesh(b,Coords_b,dim,geom,'b')

	if save=="y": 
		plt.savefig('Marker_Geometry.png',dpi=150)
	
	plt.xlabel('x')
	plt.ylabel('y')
	plt.grid()
	plt.show()	
	plt.close()

def Read_Mesh(a,marker,dim):
	# Get the mesh data
	Meshdata=SU2.mesh.tools.read(a)
	if dim=="2D":
		# Extract the marker geometry
		Points,Loop=SU2.mesh.tools.sort_airfoil(Meshdata,marker)
		# Reorder in an anticlockwise direction from trailing edge
		Foil_Points,Foil_Nodes=SU2.mesh.tools.get_markerPoints(Meshdata,marker)
		Coords=np.zeros([len(Points),2])
		for i in range(len(Points)):
			Coords[i][0]=Foil_Points[Loop[i]][0]
			Coords[i][1]=Foil_Points[Loop[i]][1]
	else:
		Coords,nodes=SU2.mesh.tools.get_markerPoints(Meshdata,marker)
	return Coords

def Plot_Mesh(Design,Coords,dim,geom,num):
	Coords=np.transpose(Coords)
	if dim=='2D':
		plt.plot(Coords[0],Coords[1],label="Design "+Design)
	
	else:
		if num=='a':
			geom.scatter(Coords[0],Coords[1],Coords[2],c='r',label='mesh_a')
		else:
			geom.scatter(Coords[0],Coords[1],Coords[2],c='b',label='mesh_b')

	plt.legend()
	plt.title('Marker Geometry')

	return

if __name__=="__main__":
	Main()