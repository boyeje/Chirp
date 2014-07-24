"""PyAudio Example: Play a wave file (callback version)."""

import pyaudio
import wave
import time
import sys
import struct
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

global i,framesint
framesint=np.array([])
i=0

# define callback (2)
def callback(in_data, frame_count, time_info, status):
    data ='\x00\x00'*wf.getnchannels()*frame_count#wf.readframes(frame_count)
    global i,framesint
    i=i+1
    framesint=np.concatenate((framesint,np.array(struct.unpack("%dh" % (frame_count), in_data)))) 
    
    return (data,pyaudio.paContinue)

# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,input=True,
                stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
#while stream.is_active():
#    time.sleep(0.1)
time.sleep(3)

# stop stream (6)
stream.stop_stream()
stream.close()
wf.close()

plt.plot(framesint)
plt.show()

# close PyAudio (7)
p.terminate()
