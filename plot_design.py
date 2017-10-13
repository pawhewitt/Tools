# CST generator
import sys,os
from optparse import OptionParser
sys.path.append(os.environ['SU2_RUN'])
import SU2 # import all the python scripts in /usr/local/SU2_RUN/SU2_PY/SU2
import numpy as np
import matplotlib.pyplot as plt
import csv


def main():

	parser=OptionParser()
	parser.add_option("-d",dest="design",help="Number of the design to be plotted")
	options,args=parser.parse_args()
	design=int(options.design)
	# Design path
	path="./DESIGNS/DSN_{:03d}/".format(design)
	# Create a folder to store the plots
	Results_Folder(design)
	# Read config

	# To do --- No need to read in config or mesh, the surface_flow
	## file has the coords as well. Check that these coords are actaully 
	# the new ones. 
	config=Read_Config(path)
	# Get all the required data
	data=Get_Design(config,path)
	#print data
	# Plot the geometric and adjoint sensitivities
	Plot_Sens(path)
	# Plot the current gradient
	Plot_Grad(path)
	# Plot the geometry
	#Plot_Pressure(path)
	# Plot the convergence history of the adjoint, Cl and Cd
	Plot_History(path)

def Results_Folder(design):
	os.system("mkdir Design"+str(design)+"_Plots")
	return

def Read_Config(path):
	config=SU2.io.config.Config(path+"DIRECT/config_CFD.cfg")
	return config

def Get_Design(config,path):
	coords=Read_Mesh(config,path)
	pressure=Get_Pressure(path)
	data={'coords':coords}
	return data


def Plot_Sens(path):
	return

def Plot_Grad(path):
	return
def Get_Pressure(path):
	with open(path+"DIRECT/surface_flow.csv") as f:
		pressure=csv.reader(f)
		for i in pressure:
			print i
	print pressure
	return pressure

	return
def Plot_History(path):
	return

def Read_Mesh(config,path):

	# get name of surface marker (airfoil, AIRFOIL etc)
	marker=config['DEFINITION_DV']['MARKER'][0][0]
	mesh=path+config['MESH_FILENAME']
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


if __name__ == '__main__':
	main()



