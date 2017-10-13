# Compares the results of two designs
# Plots the geometric differences as well as the change in ob_f up to that design
import sys,os
from optparse import OptionParser
sys.path.append(os.environ['SU2_RUN'])
import SU2 # import all the python scripts in /usr/local/SU2_RUN/SU2_PY/SU2
import numpy as np
import matplotlib.pyplot as plt
import cPickle as pickle

def Main():

	parser=OptionParser()
	parser.add_option("-a",dest="design1",help="Number of the first design")
	parser.add_option("-b",dest="design2",help="Number of the second design")
	(options,args)=parser.parse_args()
	a=int(options.design1)
	b=int(options.design2)

	path1="./DESIGNS/DSN_{:03d}/".format(a)
	path2="./DESIGNS/DSN_{:03d}/".format(b)

	config_data=Read_Config(path1)

	# Get the Files names
	Design1=Read_Mesh(config_data,path1)
	Design2=Read_Mesh(config_data,path2)
	# Plot the Geometries
	Plot_Designs(a,b,Design1,Design2)

	# Plot the obf_f and constraints 
	Plot_Funcs(a,b)

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

def Plot_Designs(a,b,Design1,Design2):
	design1=np.transpose(Design1)
	design2=np.transpose(Design2)
	plt.plot(design1[0],design1[1],'g',lw=2,label='Design'+str(a))
	plt.plot(design2[0],design2[1],'b',lw=2,label='Design'+str(b))
	plt.grid()
	plt.legend()
	plt.title('Geometry Change')
	plt.savefig('Geometry_Changes'+str(a)+'_to_'+str(b)+'.png',dpi=150)
	plt.close()


	return



def Plot_Funcs(a,b):
	results=SU2.io.load_data('results.pkl')
	lift=results.FUNCTIONS.LIFT[(a-1):(b)]
	drag=results.FUNCTIONS.DRAG[(a-1):(b)]

	fig,ax1=plt.subplots()
	ax2=ax1.twinx()
	ax1.plot(lift,'g-',lw=3)
	ax2.plot(drag,'b-',lw=3)
	ax1.set_xlabel('Design number')
	ax1.set_ylabel('Cl',color='g')
	ax2.set_ylabel('Cd',color='b')
	ax1.grid()
	plt.title('Function Change')

	major_ticks = np.arange(plt.xlim()[1])
	ax1.set_xticks(major_ticks)                                                                                                          
	


	plt.savefig('Function_Changes_Design'+str(a)+'_to_'+str(b)+'.png',dpi=150)
	plt.close()

	return

if __name__ == '__main__':
	Main()