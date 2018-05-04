# Exports plots of the adjoint, design geometry, geometric sensitivities
# the gradient and the pressure distribution
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
	config=Read_Config(path)
	# To do --- No need to read in config or mesh, the surface_flow
	## file has the coords as well. Check that these coords are actaully 
	# the new ones. 
	# Get all the required data
	data=Get_Design(path,config)
	# Plot the Data
	Plot_Data(data,design)
	#print data
	# Plot the geometric and adjoint sensitivities if available
	#Plot_Sens(path)
	# Plot the current gradient if available
	#Plot_Grad(path)
	# Plot the geometry and pressure
	#Plot_Pressure(path)
	# Plot the convergence history of the adjoint, Cl and Cd
	#Plot_History(path)

def Results_Folder(design):
	os.system("mkdir Design"+str(design)+"_Plots")
	return

def Read_Config(path):
	config=SU2.io.config.Config(path+"DIRECT/config_CFD.cfg")
	return config

def Get_Design(path,config):
	pressure,coords=Get_Pressure(path)
	# Check if gradient info is avaiable for this design
	# Need to generalise this for all Obj_f
	if os.path.isdir(path+'ADJOINT_DRAG'):
		path=path+'ADJOINT_DRAG'
		Sens=Get_Sens(path,config)
		Conv=Get_Conv(path)
	elif os.path.isdir(path+'ADJOINT_LIFT'):
		path=path+'ADJOINT_LIFT'
		Sens=Get_Sens(path,config)
		Conv=Get_Conv(path)
	data={'pressure':pressure,
		  'sens':Sens,
		  'coords':coords
		  }

	return data


def Get_Sens(path,config):

	# Get the Gradient
	with open(path+'/of_grad_cd.vtk') as f:
		csvread=csv.reader(f)
		# Skip Headers
		next(csvread,None)
		sens_grad=[]
		for row in csvread:
			sens_grad.append(row[1])
	# Sort gradients into surfaces
		sens_grad_lower=[]
		sens_grad_upper=[]
		for i in range(len(sens_grad)):
			if config['DV_PARAM']['PARAM'][i][0]==0:
				sens_grad_lower.append(sens_grad[i])
			else:
				sens_grad_upper.append(sens_grad[i])

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
	sens_geo=np.loadtxt(open(path+"/Geo_Sens.csv", "rb"), delimiter=",", skiprows=1)
	# Remove the first element from each Parameter
	
	Sens_Geo=np.zeros(shape=(len(sens_geo),(len(sens_geo[0])-1)))
	for i in range(len(sens_geo)):
		Sens_Geo[i]=np.delete(sens_geo[i],[0])

	Sens={'gradient_lower':sens_grad_lower,
				'gradient_upper':sens_grad_upper,
		  'adjoint':sens_adj,
		  'geometric':Sens_Geo}

	return Sens


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
		coords=np.column_stack((x,y))
		
	return pressure,coords

def Get_Conv(path):
	# Get the convergence history for the drag, lift and adjoint
	return

def Plot_Data(data,design):
	# plot the Gradient
	plt.plot(data['sens']['gradient_upper'],label='Gradient_Upper')
	plt.plot(data['sens']['gradient_lower'],label='Gradient_Lower')
	plt.grid()
	plt.legend()
	plt.title('Design Gradient')
	plt.savefig('Design'+str(design)+'_Plots/Gradients.png',dpi=150)
	plt.close()

	# plot the adjoint sensitivities
	plt.plot(data['sens']['adjoint'],label='Adjoint')
	plt.grid()
	plt.legend()
	plt.title('Adjoint Sensitivities')
	plt.savefig('Design'+str(design)+'_Plots/Adjoints.png',dpi=150)
	plt.close()

	# plot the Geometric Sensitivities
	i=0
	for var in data['sens']['geometric']:
		plt.plot(var,label='var '+str(i))
		i+=1
	plt.legend()
	plt.title('Geometric Sensitivities')
	plt.grid()
	plt.savefig('Design'+str(design)+'_Plots/GeoSens.png',dpi=150)
	plt.close()

	# Plot the geometry
	coords=np.transpose(data['coords'])
	plt.plot(coords[0],coords[1])
	plt.title('Geometry')
	plt.grid()
	plt.savefig('Design'+str(design)+'_Plots/Geometry.png',dpi=150)
	plt.close()

	# Plot the pressure 
	
	plt.plot(coords[0],data['pressure'])
	plt.title('Lift Cofficient')
	plt.grid()
	plt.gca().invert_yaxis()
	plt.savefig('Design'+str(design)+'_Plots/Pressure.png',dpi=150)
	plt.close()

if __name__ == '__main__':
	main()



