

"""PyAudio example: Record a few seconds of audio and save to a WAVE file."""

import matplotlib.pyplot as plt
import pyaudio
import wave
import calcbytes as cb
import numpy as np
import struct
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 1
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
		output=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []
framesint=np.array([])

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    framesint=np.concatenate((framesint,np.array(struct.unpack("%dh" % (CHUNK), data)))) 
    
    frames.append(data)
	
print("* done recording")


stream.stop_stream()
stream.close()
p.terminate()


plt.plot(framesint)
plt.show()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

#if __name__ == '__main__':
#	main()

