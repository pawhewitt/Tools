# CST_Fit 
"""
Script to fit CST curve to aerofoil coordinates and create a new mesh and config file 

"""

import sys,os
from optparse import OptionParser
sys.path.append(os.environ['SU2_RUN'])
import SU2 # import all the python scripts in /usr/local/SU2_RUN/SU2_PY/SU2
import numpy as np
from math import factorial as fac
import matplotlib.pyplot as plt
from scipy.optimize import fmin_slsqp

# TODO

# Check this works with the rae case

# TODO




def main():

	parser=OptionParser()
	parser.add_option("-f",dest="filename")
	parser.add_option("--n1",dest="n1",default="0.5")
	parser.add_option("--n2",dest="n2",default="1.0")
	# option bug to export data and make plots
	parser.add_option("--bug",dest="bug",default=False)
	
	(options, args)=parser.parse_args()
	
	filename=options.filename
	n1=float(options.n1)
	n2=float(options.n2)
	bug=bool(options.bug)

	######  Read Config  ##########
	Config=Read_Config(filename)

	###### Make the config file for SU2_DEF #########	
	#### Intially used to create mesh_motion.dat which will
	### contain the initial surface coordinates
	Config['MESH_OUT_FILENAME']=Config["MESH_FILENAME"][:-4]+"_CST.su2"
	Config['MOTION_FILENAME']='mesh_motion.dat'
	Config['MARKER_MOVING']=Config['DEFINITION_DV']['MARKER'][0][0]
	Config['DV_KIND']='SURFACE_FILE'

	# Need to get this to change param to a single element
	# Config['DV_PARAM']={0}

	SU2.io.config.dump_config('temp_def.cfg',Config) 

	# Export initial coorinates to mesh_motion.dat file ###
	os.system("SU2_DEF temp_def.cfg")

	############ Get Order of Bernstein polynomials #######333
	# Order determined by the number of design variables supplied
	# Note that it's assumed that the order is identical for both surfaces
	Order=int(0.5*len(Config['DEFINITION_DV']['PARAM'])-1)
	
	############ read coordinates  ###############
	U_Coords,L_Coords,Nodes_Order=Get_Coords(Config) 

	########## compute the fitted weights ########
	Au,Al=Compute_Coeffs(U_Coords[:,1:3],L_Coords[:,1:3],Order,n1,n2,bug)

	# ####### Export the mesh motion file ##########
	Mesh_Motion(n1,n2,Au,Al,U_Coords,L_Coords,Nodes_Order)

	# ###### Create new mesh file ########
	os.system("SU2_DEF temp_def.cfg")


	####### Make config file containing CST Weights and points to CST ######

	# SU2_DEF requires DV array 
	dvs=[0.0]*(len(Au)+len(Al))

	Config.unpack_dvs(dvs)

	cst_filename=filename[:-4]+"_CST.cfg"


	j=0
	k=0
	for i in range(len(Au)*2):
		if Config['DEFINITION_DV']['PARAM'][i][0]==1:
			Config['DEFINITION_DV']['PARAM'][i][1]=Au[j]
			Config['DEFINITION_DV']['KIND'][i]="CST"
			j+=1
		else:
			Config['DEFINITION_DV']['PARAM'][i][1]=Al[k]
			Config['DEFINITION_DV']['KIND'][i]="CST"
			k+=1

	# Point to new mesh
	Config['MESH_FILENAME']=Config["MESH_FILENAME"][:-4]+"_CST.su2"


	SU2.io.config.dump_config(cst_filename,Config) 

	### Remove Unnessary files
	os.remove("temp_def.cfg")
	os.remove("mesh_motion.dat")
 


	###### Plot data if bug option is True #######
	# # plot the points showing how the foils differ and by how much
	# Plot the component Aerofoils, the bernstein Polynomials
	# and the L2 norm over the chord

	if bug==True:	
		Plot(U_Coords[:,1:3],L_Coords[:,1:3],Au,Al,n1,n2)

def Mesh_Motion(n1,n2,Au,Al,U_Coords,L_Coords,Nodes_Order):
	# Evaluate CST

	opf1=open("mesh_motion.dat",'w')

	CST_U=CST(U_Coords[:,1:3],Au,n1,n2)

	CST_L=CST(L_Coords[:,1:3],Al,n1,n2)

	CST_Coords=np.concatenate((CST_U,CST_L))
	Coords=np.concatenate((U_Coords,L_Coords))

	for i in range(len(CST_Coords)):
		Nodes_ID=int(Nodes_Order[i])
		for j in range(len(CST_Coords)):
			if (Coords[j][0]==Nodes_Order[i]):
				opf1.write("{}\t {:8.12f}\t {:8.12f} \n".format(Nodes_ID,CST_Coords[j][0],CST_Coords[j][1]))

	opf1.close()

def Read_Config(filename):
	Config=SU2.io.config.Config(filename)
	return Config

def Get_Coords(Config):

	Coords=np.loadtxt('mesh_motion.dat',delimiter='\t')

	Nodes_Order=Coords[:,0]

	# Divide coords for surfaces
	U_Coords,L_Coords=Split(Coords)

	return U_Coords,L_Coords,Nodes_Order

def Compute_Coeffs(U_Coords,L_Coords,Order,n1,n2,bug):
	# initial coefficents set for upper (u) and lower (l) surfaces
	Au=np.ones(Order+1)# one more than the order
	Al=np.ones(Order+1)*-1 
	
	if bug==True:
		iprint=3
	else:
		iprint=0

	# Upper
	Au=fmin_slsqp(Get_L2,Au,args=(U_Coords,n1,n2),iprint=iprint)
	# Lower
	Al=fmin_slsqp(Get_L2,Al,args=(L_Coords,n1,n2),iprint=iprint)

	return Au,Al #,CST_Lower # See how to group this together 

def Bi_Coeff(Order): 
	#compute the binomial coefficient
	K=np.zeros(Order+1)
	for i in range(len(K)):
		K[i]=fac(Order)/(fac(i)*(fac(Order-i)))
	return K


def C_n1n2(Coords,n1,n2): 
	# class function
	C=np.zeros(len(Coords))
	for i in range(len(C)):
		C[i]=(Coords[i][0]**n1)*(1-Coords[i][0]**n2)
	return C

def Total_Shape(Coords,A): 
	# Order of the bernstein polynomial 
	Order=len(A)-1
	# Total shape function
	S=np.zeros(len(Coords))
	# Component Shape Function
	S_c=Comp_Shape(Coords,Order)

	S_c=np.transpose(S_c)
	for  i in range(len(Coords)):
		S[i]+=np.dot(A,S_c[i])

	return S

def Comp_Shape(Coords,Order):
	# Component Shape function
	K=Bi_Coeff(Order)
	# compute the Binomial Coefficient
	S_c=np.zeros([Order+1,len(Coords)])

	for i in range(Order+1): # order loop
		for j in range(len(Coords)): # point loop
			S_c[i][j]=(K[i]*(Coords[j][0]**i))*((1-Coords[j][0])**(Order-i))
	
	return S_c

def CST(Coords,A,n1,n2): 
	CST_Coords=np.zeros([len(Coords),2])
	# Compute Class Function
	C=C_n1n2(Coords,n1,n2)

	# Compute the Shape Function
	S=Total_Shape(Coords,A)
	# evaluate the CST function
	for i in range(len(Coords)):
		CST_Coords[i][1]=C[i]*S[i]
		# Store 
		CST_Coords[i][0]=Coords[i][0]

	return CST_Coords

def Get_L2(A,Coords,n1,n2): 

	CST_Coords=CST(Coords,A,n1,n2)

	# Calculate the current L2 norm 
	L2=np.linalg.norm(CST_Coords - Coords,ord=2)
	return L2

def Split(Coords):
		# Spilt the surfaces according to the z component of the normal

	L_Coords=[]
	U_Coords=[]

	Normals=Get_Normal(Coords[:,1:3])
	
	for i in range(len(Coords)):
		if Normals[i][1]<0:
			L_Coords.append(Coords[i])
		else:
			U_Coords.append(Coords[i])

	# # Convert to numpy array
	L_Coords=np.array(L_Coords)
	U_Coords=np.array(U_Coords)

	return U_Coords,L_Coords

def Get_Normal(Coords):
	# Compute the normals

	Normals=np.zeros([len(Coords),2])
	for i in range(len(Coords)):
		if i==0:
			dx_1=Coords[i][0]-Coords[len(Coords)-1][0]
			dy_1=Coords[i][1]-Coords[len(Coords)-1][1]
			dx_2=Coords[i+1][0]-Coords[i][0]
			dy_2=Coords[i+1][1]-Coords[i][1]
		
		elif i==len(Coords)-1:
			dx_1=Coords[i][0]-Coords[i-1][0]
			dy_1=Coords[i][1]-Coords[i-1][1]
			dx_2=Coords[0][0]-Coords[i][0]
			dy_2=Coords[0][1]-Coords[i][1]

		else:
			dx_1=Coords[i][0]-Coords[i-1][0]
			dy_1=Coords[i][1]-Coords[i-1][1]
			dx_2=Coords[i+1][0]-Coords[i][0]
			dy_2=Coords[i+1][1]-Coords[i][1]
	
		norm_1=-dy_1,dx_1
		norm_2=-dy_2,dx_2

		Normals[i][0]=0.5*(norm_1[0]+norm_2[0])
		Normals[i][1]=0.5*(norm_1[1]+norm_2[1])

	return Normals

def Plot(U_Coords,L_Coords,Au,Al,n1,n2):


	u_coords=np.transpose(U_Coords)
	l_coords=np.transpose(L_Coords)
	
	CST_Upper=CST(U_Coords,Au,n1,n2)
	CST_Lower=CST(L_Coords,Al,n1,n2)

	cst_upper=np.transpose(CST_Upper)
	cst_lower=np.transpose(CST_Lower)

	###### Plot base and CST aerofoils #######

	fig=plt.figure()
	ax=fig.add_subplot(1,1,1)

	
	plt.plot(cst_upper[0],cst_upper[1],'o',label='CST',color='blue',markersize=5)
	plt.plot(cst_lower[0],cst_lower[1],'o',color='blue',markersize=5)
	

	plt.plot(u_coords[0],u_coords[1],label='Baseline',color='green')
	plt.plot(l_coords[0],l_coords[1],color='green')

	plt.grid()
	ax.legend(loc='best')
	ax.set_xlabel('x/c')
	ax.set_ylabel('z/c')
	plt.title('Curve Fitting')
	
	filename='./Foils_Plot.png'
	plt.savefig(filename,dpi=150)
	plt.close()

	######## Plot Bernstein Functions ########

	Order=len(Au)-1
	Su_c=Comp_Shape(U_Coords,Order)
	Sl_c=Comp_Shape(L_Coords,Order)

	fig=plt.figure()
	ax=fig.add_subplot(1,1,1)
	for i in range(len(Su_c)):
		S_c=np.transpose(Su_c[i])
		plt.plot(u_coords[0],S_c)

	plt.grid()
	plt.title('Bernstein Shape Functions')
	filename='./Berstein_Plot.png'
	plt.savefig(filename,dpi=150)
	plt.close()


	########## Plot Component Aerofoils ######


	fig=plt.figure()
	ax=fig.add_subplot(1,1,1)

	C=C_n1n2(U_Coords,n1,n2)
	Comp=np.zeros(len(U_Coords))
	for i in range(len(Su_c)):		
		for j in range(len(U_Coords)):
			Su_c[i][j]=Su_c[i][j]*Au[i]
			Comp[j]=C[j]*Su_c[i][j]
		plt.plot(u_coords[0],Comp,color='red')

	plt.plot(u_coords[0],cst_upper[1],color='blue')

	C=C_n1n2(L_Coords,n1,n2)
	Comp=np.zeros(len(L_Coords))
	for i in range(len(Sl_c)):		
		for j in range(len(L_Coords)):
			Sl_c[i][j]=Sl_c[i][j]*Al[i]
			Comp[j]=C[j]*Sl_c[i][j]
		plt.plot(l_coords[0],Comp,color='red')

	plt.plot(l_coords[0],cst_lower[1],color='blue')
	plt.grid()
	plt.title('CST Component Aerofoils')
	filename='./CST_Foils.png'
	plt.savefig(filename,dpi=150)
	plt.close()



	return
# this is only accessed if running from command prompt
if __name__ == '__main__':
    main()
