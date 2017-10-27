# CST generator
import sys,os
from optparse import OptionParser
sys.path.append(os.environ['SU2_RUN'])
import SU2 # import all the python scripts in /usr/local/SU2_RUN/SU2_PY/SU2
import numpy as np
from math import factorial as fac
import matplotlib.pyplot as plt
from scipy.optimize import fmin_slsqp

# TODO

# Need to modify for the rae case
# Think that the airfoil coordinates are anti-clockwise
# in the mesh file rather than clockwise.  

# TODO




def main():

	parser=OptionParser()
	parser.add_option("-f",dest="filename",default="inv_NACA0012.cfg")
	parser.add_option("--n1",dest="n1",default="0.5")
	parser.add_option("--n2",dest="n2",default="1.0")
	# parser.add_option("--c",dest="fit",default=False)
	(options, args)=parser.parse_args()
	
	filename=options.filename
	n1=float(options.n1)
	n2=float(options.n2)
	# Read Config 
	Config=Read_Config(filename)
	# Order determined by the number of design variables supplied
	# Note that it's assumed that the order is identical for both surfaces
	Order=int(0.5*len(Config['DEFINITION_DV']['PARAM'])-1)
	# read coordinates
	U_Coords,L_Coords=Read_Mesh(Config) # mesh/DAT filename
	
	# compute the coefficients
	Au,Al=Compute_Coeffs(U_Coords,L_Coords,Order,n1,n2)

	dvs=[0.0]*(len(Au)+len(Al))

	# # Update Config File

	Update_Config(filename,Config,Au,Al,dvs) 

	# # plot the points showing how the foils differ and by how much

	Plot(U_Coords,L_Coords,Au,Al,n1,n2)
	

	# TODO
	# Why are the x components different in the CST and 
	# the original foil for the RAE?

	# # re-mesh geometry
	Re_Mesh(filename)

def Update_Config(filename,Config,Au,Al,dvs):

	Config.unpack_dvs(dvs)

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
	#SU2.io.config.write_config(Config,Config_Data)
	SU2.io.config.dump_config(filename,Config)
	return

def Read_Config(filename):
	Config=SU2.io.config.Config(filename)
	print Config
	#Config_Data=SU2.io.config.read_config(Config
	return Config

def Read_Mesh(Config):

	# Mesh Filename
	Mesh=Config['MESH_FILENAME']
	marker=Config['DEFINITION_DV']['MARKER'][0][0]

	# Using the Su2 python scripts for reading mesh
	Meshdata=SU2.mesh.tools.read(Mesh) # read the mesh

	# sort airfoil coords to be arrange clockwise from trailing edge
	Points,Loop=SU2.mesh.tools.sort_airfoil(Meshdata,marker)
	
	# get the points for the surface marker
	Foil_Points,Foil_Nodes=SU2.mesh.tools.get_markerPoints(Meshdata,marker)

	#Get the sorted points 
	Coords=np.zeros([len(Points),2])
	for i in range(len(Points)):
		Coords[i][0]=Foil_Points[Loop[i]][0]
		Coords[i][1]=Foil_Points[Loop[i]][1]
	# Divide coords for surfaces
	U_Coords,L_Coords=Split(Coords)

	return U_Coords,L_Coords

def Compute_Coeffs(U_Coords,L_Coords,Order,n1,n2):
	# initial coefficents set for upper (u) and lower (l) surfaces
	Au=np.ones(Order+1)# one more than the order
	Al=np.ones(Order+1)*-1 
	
	# Upper
	Au=fmin_slsqp(Get_L2,Au,args=(U_Coords,n1,n2),iprint=0)
	# Lower
	Al=fmin_slsqp(Get_L2,Al,args=(L_Coords,n1,n2),iprint=0)

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
		CST_Coords[i][0]=Coords[i][0]

	return CST_Coords

def Get_L2(A,Coords,n1,n2): 

	CST_Coords=CST(Coords,A,n1,n2)

	# Calculate the current L2 norm 
	L2=np.linalg.norm(CST_Coords - Coords,ord=2)
	return L2

def Split(Coords):
		# Spilt the surfaces according to the z component of the normal

	U_Coords=[]
	L_Coords=[]
	Normals=Get_Normal(Coords)

	for i in range(len(Coords)):
		if Normals[i][1]<0:
			L_Coords.append(Coords[i])
		else:
			U_Coords.append(Coords[i])

	# Convert to numpy array
	L_Coords=np.array(L_Coords)
	U_Coords=np.array(U_Coords)

	return U_Coords,L_Coords

def Get_Normal(Coords):
	# Compute the normals

	# TODO 
	# Clean this up

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

def Write_File(): 
	# Write a file containing the coefficients 
	return

def Re_Mesh(filename): # Mesh the geometry according to the CST approximation.
		os.system("SU2_DEF "+filename)

def Plot(U_Coords,L_Coords,Au,Al,n1,n2):

	u_coords=np.transpose(U_Coords)
	l_coords=np.transpose(L_Coords)
	
	CST_Upper=CST(U_Coords,Au,n1,n2)
	CST_Lower=CST(L_Coords,Al,n1,n2)

	cst_upper=np.transpose(CST_Upper)
	cst_lower=np.transpose(CST_Lower)


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

	# temp - print out coords to compare with DEF mesh 
	Coords=np.append(CST_Upper,CST_Lower,axis=0)
	np.savetxt("CST_Coords.dat",Coords)

	return
# this is only accessed if running from command prompt
if __name__ == '__main__':
    main()
