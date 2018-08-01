import matplotlib.pyplot as plt
import numpy as np

# Read from file
data=np.loadtxt('surface_adjoint.csv',delimiter=',',skiprows=2)

#data=np.transpose(data)

# Reorder according to first point I.D.'s in first column
data=sorted(data,key=lambda x:x[0])

data=np.transpose(data)

# Find Leading Edge Turning Point
for i in range(len(data[0])):
	if data[6][i]<0.2:
		if data[7][i]>0:
			point=i
			break

lower=[]
upper=[]

# Split Surfaces
for i in range(len(data[0])):
	if i<point:
		lower.append(([data[6][i],data[1][i]]))
	else:
		upper.append([data[6][i],data[1][i]])

lower=np.transpose(lower)
upper=np.transpose(upper)

plt.plot(lower[0],lower[1],color='blue',label='lower surface')
plt.plot(upper[0],upper[1],color='green',label='upper surface')

plt.grid()
plt.title('Adjoint Surface Sensitivities')
plt.ylabel('Sensitivity (df/dx)')
plt.xlabel('(x/c)')
plt.xlim([0,1])
plt.ylim([-1.5,1.5])
plt.legend()
plt.savefig('adjoint_plot',dpi=150)
plt.show()
