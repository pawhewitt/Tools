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
	#Results_Folder(design)
	# Read config

	# To do --- No need to read in config or mesh, the surface_flow
	## file has the coords as well. Check that these coords are actaully 
	# the new ones. 
	# Get all the required data
	data=Get_Design(path)
	#print data
	# Plot the geometric and adjoint sensitivities if available
	#Plot_Sens(path)
	# Plot the current gradient if available
	#Plot_Grad(path)
	# Plot the geometry and pressure
	#Plot_Pressure(path)
	# Plot the convergence history of the adjoint, Cl and Cd
	Plot_History(path)

def Results_Folder(design):
	os.system("mkdir Design"+str(design)+"_Plots")
	return

def Read_Config(path):
	config=SU2.io.config.Config(path+"DIRECT/config_CFD.cfg")
	return config

def Get_Design(path):
	pressure=Get_Pressure(path)
	# Check if gradient info is avaiable for this design
	# Need to generalise this for all Obj_f
	if os.path.isdir(path+'ADJOINT_DRAG'):
		path=path+'ADJOINT_DRAG'
		Sens=Get_Sens(path)
	elif os.path.isdir(path+'ADJOINT_LIFT'):
		path=path+'ADJOINT_LIFT'
		Sens=Get_Sens(path)
	data={'pressure':pressure}

	return data


def Get_Sens(path):
	sens_geo=[]

	# Get the Gradient
	with open(path+'/of_grad_cd.vtk') as f:
		csvread=csv.reader(f)
		# Skip Headers
		next(csvread,None)
		sens_grad=[]
		for row in csvread:
			sens_grad.append(row[1])

	# Get the Adjoint Sens
	with open(path+'/surface_adjoint.csv') as f:
		csvread=csv.reader(f)
		# skip header
		next(csvread,None)
		next(csvread,None)
		sens_adj=[]
		for row in csvread:
			sens_adj.append(row[1])
	# Get the Geometric Sensitivities
	

	#Sens=np.column_stack((sens_geo,sens_adj,sens_grad))

	return

def Plot_Grad(path):
	return
def Get_Pressure(path):
	with open(path+"DIRECT/surface_flow.csv") as f:
		csvread=csv.reader(f)
		# Skip the headers
		next(csvread,None)
		x=[]
		y=[]
		pressure=[]
		for row in csvread:
			x.append(row[1])
			y.append(row[2])
			pressure.append(row[4])
		# Merge arrays into a matrix
		pressure=np.column_stack((x,y,pressure))
	return pressure

	return
def Plot_History(path):
	return

if __name__ == '__main__':
	main()



