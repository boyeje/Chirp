import numpy as np
import time
import math
import matplotlib.pyplot as plt #ralenti fortement le script
from scipy.signal import * #permet l'utilisation de scipy.signal.chirp(t, f0=0, t1=1, f1=100, method='linear', phi=0, qshape=None)
time_base=np.arange(0,0.5,1.0/44100)
time_base4=np.arange(-1,4,1.0/44100)# 2000hz echantillonage
time_base4_true=np.arange(0,3,1.0/44100)#ne pas oublier que 1/44100=0 

print "Import finished"
#chirp220to3520=np.array([])
chirp220to440=np.array([]) #creation du chirp vide
chirpto440_decal=np.zeros(time_base4_true.size)
i=0
for t in np.nditer(time_base): #boucle for sur un array
	#chirp220to3520=np.concatenate((chirp220to3520,np.array([chirp(t,220,1,3520)])))
	chirp220to440=np.concatenate((chirp220to440,np.array([chirp(t,10,0.5,100)])))
	chirpto440_decal[44100+i]=chirp(t,10,0.5,100) 
	i=i+1
#plt.plot(time_base,chirp220to440)
#plt.plot(time_base4,chirpto440_decal)

noise=6*np.random.rand(chirpto440_decal.size)-3
realSound=chirpto440_decal+noise
start=time.time()
norm_sound=math.sqrt((realSound*realSound).sum())
norm_chirp220to440=math.sqrt((chirp220to440*chirp220to440).sum())
duration=time.time()-start 
print duration
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

start=time.time()
print len(realSound)
print len(chirp220to440)
#corr=np.correlate(realSound,chirp220to440)/norm_chirp220to440*norm_sound
duration=time.time()-start 
start=time.time()
conv=fftconvolve(realSound,chirp220to440[::-1],mode='valid')/(norm_chirp220to440*norm_sound)
convEnv=conv[argrelmax(conv,order=10)]
duration2=time.time()-start 
#print cor.size
#print time_base4_true.size
#plt.plot(corr)
print len(conv)
print len(time_base4_true)
plt.subplot(212)
plt.plot(convEnv[400:650])
#plt.subplot(211)
#plt.plot(conv[20000:70000])
print duration
print duration2
plt.show()
 
#chirp220to440[-1:-(chirp220to440.size+1):-1] inverse l'array 
