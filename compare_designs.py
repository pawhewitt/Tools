# Compares the results of two designs
# Plots the geometric differences as well as the change in ob_f up to that design
import sys,os
from optparse import OptionParser
sys.path.append(os.environ['SU2_RUN'])
import SU2 # import all the python scripts in /usr/local/SU2_RUN/SU2_PY/SU2
import numpy as np
import matplotlib.pyplot as plt

def Main():

	parser=OptionParser()
	parser.add_option("--d1",dest="design1")
	parser.add_option("--d2",dest="design2")
	(options,args)=parser.parse_args()
	design1=options.design1
	design2=options.design2

	path1="./DESIGNS/DSN_{:03d}/".format(int(design1))
	path2="./DESIGNS/DSN_{:03d}/".format(int(design2))

	config_data=Read_Config(path1)

	# Get the Files names
	Design1=Read_Mesh(config_data,path1)
	Design2=Read_Mesh(config_data,path2)
	# Plot the Geometries
	Plot_Designs(Design1,Design2)

	# Plot the obf_f and constraints 
	#Plot_Funcs(design)

def Read_Config(path1):
	config_data=SU2.io.config.Config(path1+"/config_DSN.cfg")
	return config_data

def Read_Mesh(config_data,path):
	# get name of surface marker (airfoil, AIRFOIL etc)
	marker=config_data['DEFINITION_DV']['MARKER'][0][0]
	# filename of initial (meshfile_1) and deformed mesh (meshfile_2)
	if (path[-2]=='1'):
		mesh=path+config_data['MESH_FILENAME']
	else:
		mesh=path+config_data['MESH_FILENAME'][:-4]+"_deform.su2"
	
	# # Using the Su2 python scripts for reading mesh
	Meshdata=SU2.mesh.tools.read(mesh) # read the mesh

	# sort airfoil coords to be arrange clockwise from trailing edge
	Points,Loop=SU2.mesh.tools.sort_airfoil(Meshdata,marker)
	
	# get the points for the surface marker
	Foil_Points,Foil_Nodes=SU2.mesh.tools.get_markerPoints(Meshdata,marker)

	#Get the sorted points 
	Coords=np.zeros([len(Points),2])
	for i in range(len(Points)):
		Coords[i][0]=Foil_Points[Loop[i]][0]
		Coords[i][1]=Foil_Points[Loop[i]][1]

	return Coords

def Plot_Designs(Design1,Design2):
	design1=np.transpose(Design1)
	design2=np.transpose(Design2)
	plt.plot(design1[0],design1[1])
	plt.plot(design2[0],design2[1])
	plt.show()

	return



def Plot_Funcs(design):
	return









if __name__ == '__main__':
	Main()