'''
Autor : Simon
Date  : 17.07.2014
Title : filter_test.py
Resume: A script to test filter config
'''

import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal

########################################################################

def generate_sin(time_base, f):
	return np.sin(2*np.pi*f*time_base)
	
def generate_chirp(RATE, len_chirp, f0, f1):
	dt = 1.0/RATE
	time_base = np.arange(0, len_chirp, dt)
	my_chirp = scipy.signal.chirp(time_base, f0, len_chirp, f1)
	return my_chirp

########################################################################


# Define Frequency
fe = 44100
dt =1.0/fe
f0=7000
f1=8000
f2=9000
# time_base=np.arange(0,2.0/f0-dt,dt)
time_base=np.arange(0,0.005,dt)
'''
# Time
# start_mod = time.time()

# Built reference sinus
s0 = generate_sin(time_base, f0)
s1 = generate_sin(time_base, f1)
s2 = generate_sin(time_base, f2)

# Built signal
zero = np.zeros((300))
A = np.concatenate((s0,s1))
for i in range (2):
	A = np.concatenate((A,A))
A = np.concatenate((s2,A))
A = np.concatenate((zero,A))
A = np.concatenate((A,s2))
A = np.concatenate((A,zero))

'''
# Chirp
fe = 44100
f0 = 7000
f1 = 9000

zero = np.zeros((300))

A = generate_chirp(fe, 0.2, f0, f1)

A = np.concatenate((zero,A))
A = np.concatenate((A,zero))

# Filter 8000Hz
N = 3
Wn=(0.35,0.38)
b, a = scipy.signal.butter(N, Wn, 'bandpass')
data_filt = scipy.signal.filtfilt(b, a, A)

data_fft = abs(np.fft.fft(data_filt, 44100))


'''
# Filter 2000Hz
N = 3
Wn=(0.08,0.1)
b, a = scipy.signal.butter(N, Wn, 'bandpass')
data_filt = scipy.signal.filtfilt(b, a, A)

data_fft = abs(np.fft.fft(data_filt, 44100))


# High pass Filter
N=6
Wn=0.04
b, a = scipy.signal.butter(N, Wn, 'high')
my_signal = scipy.signal.filtfilt(b, a, A)

# Low pass Filter
N=8
Wn=0.05
b, a = scipy.signal.butter(N, Wn, 'low')
data_filt = scipy.signal.filtfilt(b, a, my_signal)

# Absolute value
maxi=max(max(data_filt),abs(min(data_filt)))
data_filt = data_filt / abs(maxi)
my_signal_abs = abs(data_filt)
'''



f, axarr = plt.subplots(3)
axarr[0].plot(A)
axarr[0].set_title('input signal (500, 2000 & 4000 Hz)')
axarr[1].plot(data_filt)
axarr[1].set_title('filter output')
axarr[2].plot(data_fft[:10000])
axarr[2].set_title('fft')
plt.show()
