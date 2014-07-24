import numpy as np
import time
import math
import matplotlib.pyplot as plt #ralenti fortement le script
from scipy.signal import * #permet l'utilisation de scipy.signal.chirp(t, f0=0, t1=1, f1=100, method='linear', phi=0, qshape=None)
time_base=np.arange(0,0.5,1.0/44100)
time_base4=np.arange(-1,4,1.0/44100)# 2000hz echantillonage
time_base4_true=np.arange(0,1.5,1.0/44100)#ne pas oublier que 1/44100=0 

print "Import finished"
#chirp220to3520=np.array([])
chirp220to440=np.array([]) #creation du chirp vide
chirpto440_decal=np.zeros(time_base4_true.size)
i=0
for t in np.nditer(time_base): #boucle for sur un array
	#chirp220to3520=np.concatenate((chirp220to3520,np.array([chirp(t,220,1,3520)])))
	chirp220to440=np.concatenate((chirp220to440,np.array([chirp(t,2000,0.5,10000)])))
	chirpto440_decal[11025+i]=chirp(t,2000,0.5,10000) 
	i=i+1

#plt.plot(time_base,chirp220to440)
#plt.plot(time_base4,chirpto440_decal)

noise=10*np.random.rand(chirpto440_decal.size)-5
realSound=noise+chirpto440_decal
norm_sound=math.sqrt((realSound*realSound).sum())
norm_chirp220to440=math.sqrt((chirp220to440*chirp220to440).sum())
#print norm_chirp220to440
#cor=np.zeros(time_base4_true.size)


#start=time.time()
#
#for i in range(8000):
#	norm_y=(realSound[i:2000+i]*realSound[i:2000+i]).sum()+1
#	norm_y=math.sqrt(norm_y)
#	cor[i]=(chirp220to440*realSound[i:2000+i]).sum()/(norm_y*norm_chirp220to440)
#
#duration=time.time()-start 


#corr=np.correlate(realSound,chirp220to440)/norm_chirp220to440*norm_sound
start=time.time()
conv=fftconvolve(realSound,chirp220to440[::-1],mode='same')/(norm_chirp220to440*norm_sound)
peak=argrelmax(conv,order=500)
duration2=time.time()-start 


print "Diff "+str(len(peak)-len(time_base4_true))
print type(peak)
plt.plot(conv[peak])
print duration2
plt.show()
 
#chirp220to440[-1:-(chirp220to440.size+1):-1] inverse l'array 
