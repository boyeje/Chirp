import scipy.signal as ss
import scipy.fftpack as ff
import numpy as np
import matplotlib.pyplot as plt

LEN=0.2

time_base=np.arange(0,LEN,1.0/44100)

chirp=np.array([])

for t in np.nditer(time_base):
	chirp=np.concatenate((chirp,np.array([ss.chirp(t,200,LEN,8000)])))

fchirp=ff.rfft(chirp,44100)
cfchirp=np.zeros(len(fchirp)/2-1)
for i in range(len(fchirp)/2-101):
	cfchirp[i]=abs(complex(fchirp[2*i+101],fchirp[2*i+102]))


plt.plot(cfchirp)
plt.show()

filter_hz=4000
RATE=44100
b,a=ss.butter(5,filter_hz/(RATE/2.0),btype='low')
filtchirp=ss.lfilter(b,a,chirp)
plt.plot(chirp,'b')
plt.plot(filtchirp,'r')
plt.show()
