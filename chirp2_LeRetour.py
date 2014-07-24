import numpy as np
import time
import math
import matplotlib.pyplot as plt #ralenti fortement le script
from scipy.signal import * #permet l'utilisation de scipy.signal.chirp(t, f0=0, t1=1, f1=100, method='linear', phi=0, qshape=None)
time_base=np.arange(0,1,1.0/2000)
time_base4=np.arange(-1,4,1.0/2000)# 2000hz echantillonage
time_base4_true=np.arange(0,4,1.0/2000)#ne pas oublier que 1/44100=0 


#chirp220to3520=np.array([])
chirp220to440=np.array([]) #creation du chirp vide
chirpto440_decal=np.zeros(time_base4.size)
i=0
for t in np.nditer(time_base): #boucle for sur un array
	#chirp220to3520=np.concatenate((chirp220to3520,np.array([chirp(t,220,1,3520)])))
	chirp220to440=np.concatenate((chirp220to440,np.array([chirp(t,220,1,440)])))
	chirpto440_decal[6000+i]=chirp(t,220,1,440) #tu mexplique a quoi correspond 132300
	i=i+1

#plt.plot(time_base,chirp220to440)
#plt.plot(time_base4,chirpto440_decal)
norm_chirp220to440=math.sqrt((chirp220to440*chirp220to440).sum())
#print norm_chirp220to440
cor=np.zeros(time_base4_true.size)


start=time.time()


for i in range(8000):
	norm_y=(chirpto440_decal[i:2000+i]*chirpto440_decal[i:2000+i]).sum()+1
	norm_y=math.sqrt(norm_y)
	cor[i]=(chirp220to440*chirpto440_decal[i:2000+i]).sum()/(norm_y*norm_chirp220to440)

duration=time.time()-start 


#print cor.size
#print time_base4_true.size
plt.plot(time_base4,realSound)
print duration
plt.show()

#chirp220to440[-1:-(chirp220to440.size+1):-1] inverse l'array 
