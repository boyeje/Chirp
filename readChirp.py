# This program creates a chirp and play it

import pyaudio
import wave
import sys
import numpy as np
import scipy.signal as ss
import struct
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
		output=True,
		input=True,
                frames_per_buffer=CHUNK)
time_base=np.arange(0,0.1,1.0/44100)

datachirp=10240*'\x00\x00'

for t in np.nditer(time_base):
    datachirp=datachirp+struct.pack('h',int(ss.chirp(t,2000,0.1,10000)*(32767)))
#print 'Start chirp'
#start=time.time()
stream.write(datachirp,len(datachirp))  #sounds good

#while datachirp != '':                  #sounds bad
#    stream.write(datachirp,2*CHUNK)
#    datachirp=datachirp[2*CHUNK:len(datachirp)]

#duration=time.time()-start 
#print duration
print stream.get_input_latency()*44100
print stream.get_output_latency()*44100
stream.stop_stream()
stream.close()
p.terminate()
