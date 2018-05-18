### Plot mapped sensitivity values from sync folder

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from optparse import OptionParser

parser=OptionParser()
parser.add_option('-p',dest='param')
options,args=parser.parse_args()
param=int(options.param)+1

coords=np.loadtxt('/home/phewitt/Dropbox/Opt_Sync/Initial_Design.txt')
sens=np.loadtxt('/home/phewitt/Dropbox/Opt_Sync/Sens.txt',delimiter=',')

fig=plt.figure() # Create figure object
geom=fig.add_subplot(111,projection='3d')

coords=np.transpose(coords) # transpose coords for plotting

# create color_map
# find the range of sens values for the current parameter
sens=np.transpose(sens)
span=np.ptp(sens[param])
scaled_sens=sens[param]-sens[param].min()
scaled_sens=scaled_sens/scaled_sens.max()

jet= [cm.jet_r(x) for x in scaled_sens]

if len(coords)==2:
	geom.scatter(coords[0],coords[1]) 
else:
	geom.scatter(coords[0],coords[1],coords[2],c=jet) 

plt.xlabel('x')
plt.ylabel('y')

plt.show()
