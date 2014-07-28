'''
Autor : Simon
Date  : 17.07.2014
Title : noise_fft.py
Resume: Measure the noise frequency
'''

import pyaudio
import time
import numpy as np
import struct
import matplotlib.pyplot as plt
import math
import scipy.signal

########################################################################

global i, micro_input
i=0
micro_input = ''

WIDTH = 2
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

def callback(in_data, frame_count, time_info, status):
	global micro_input, i
	data = ''
	if i<100:
		flag = pyaudio.paContinue
		data = data+frame_count*'\x00\x00'
		i=i+1
	else:
		flag = pyaudio.paComplete
	
	micro_input = micro_input + in_data
	return (data, flag)

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()


nbr_of_frames = len(micro_input)/2 
data_array = np.array(struct.unpack("%dh" % (nbr_of_frames), micro_input))

data_fft=np.fft.fft(data_array,44100)

my_signal = abs(data_fft[100:44000])

plt.plot(my_signal)
plt.axis('tight')
plt.show()

