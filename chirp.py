import numpy as np
import time
import matplotlib.pyplot as plt #ralenti fortement le script
from scipy.signal import * #permet l'utilisation de scipy.signal.chirp(t, f0=0, t1=1, f1=100, method='linear', phi=0, qshape=None)
time_base=np.arange(0,1,1.0/44100) # base de temps a 44100hz (pour info un signal de 440hz necessite une fréquence d'échantillonage de 880hz, IMBECILE!!
time_base4=np.arange(-1,4,1.0/44100)
time_base4_true=np.arange(0,4,1.0/44100)#ne pas oublier que 1/44100=0 


#chirp220to3520=np.array([])
chirp220to440=np.array([]) #creation du chirp vide
chirpto440_decal=np.zeros(time_base4.size)
i=0
for t in np.nditer(time_base): #boucle for sur un array
	#chirp220to3520=np.concatenate((chirp220to3520,np.array([chirp(t,220,1,3520)])))
	chirp220to440=np.concatenate((chirp220to440,np.array([chirp(t,220,1,440)])))
	chirpto440_decal[132300+i]=chirp(t,220,1,440) #tu m'explique à quoi correspond 132300?
	i=i+1

#plt.plot(time_base,chirp220to440)
#plt.plot(time_base4,chirpto440_decal)

norm_chirp220to440=(chirp220to440*chirp220to440).sum()

cor=np.zeros(time_base4_true.size)


start=time.time()

# celui qui a demandé 176400*44100 multiplications et 2*176400 additions à l'ordi est un con
for i in range(176400):
	norm_y=(chirpto440_decal[i:44100+i]*chirpto440_decal[i:44100+i]).sum()+1
	cor[i]=(chirp220to440*chirpto440_decal[i:44100+i]).sum()/(norm_y*norm_chirp220to440)

duration=time.time()-start # la punition pour tes conneries

print cor.size
print time_base4_true.size
plt.plot(time_base4_true,cor)
print duration
plt.show()


