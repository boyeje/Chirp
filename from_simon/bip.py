'''
Autor : Simon
Date  : 23.07.2014
Title : bip.py
Resume: Play a short bip
'''

# import matplotlib.pyplot as plt
import scipy.signal
import numpy as np
import pyaudio
import struct
import time
import sys

import bits_convert_v2
import header_v3


########################################################################


def generate_sin(time_base, f):
	return np.sin(2*np.pi*f*time_base)


########################################################################

# Define stream config
RATE = 44100
CHANNELS = 1
FORMAT = pyaudio.paInt16 

# Define Frequency
fe = 44100
f0=2000
f1=8000
dt =1.0/fe
duration = 0.1
time_base=np.arange(0, duration, dt)

# Built reference sinus
s1 = generate_sin(time_base, f1)


# To string
output_str = ''
for k in s1:
	output_str = output_str + struct.pack('h',int(k*(32767)))

# Time
end_mod = time.time()

# Instantiate PyAudio
p = pyaudio.PyAudio()

# Open stream
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)
stream.start_stream()
print "Stream Start"

# Read data
data = output_str

# Play stream 
stream.write(data)
time.sleep(0.5)
'''
stream.write(data)
time.sleep(0.5)
stream.write(data)
time.sleep(0.5)'''

# Stop stream
stream.stop_stream()
stream.close()

# Close PyAudio
p.terminate()
print "Stream End"

