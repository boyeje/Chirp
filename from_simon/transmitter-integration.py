'''
Autor : Simon
Date  : 21.07.2014
Title : transmitter-bip.py
Resume: Modulate & send the message (after a bip)

Run   : python transmitter-bip.py (ID.dest) (message)
Ex    : python transmitter-bip.py 2 azerty
'''

# import matplotlib.pyplot as plt
import scipy.signal
import numpy as np
import pyaudio
import struct
import math
import time
import sys

import bits_convert_v2
import header_v3


########################################################################

def channel_coding(data, n):
	data_protec=[]
	for i in range(len(data)):
		if data[i]==1:
			for i in range(n):
				data_protec.append(1)
		else:
			for i in range(n):
				data_protec.append(0)
	return data_protec


def generate_sin(time_base, f):
	return np.sin(2*np.pi*f*time_base)


def fsk_modulation(data, s1, s0):
	FSK=[]
	for i in range(len(data)):
		if data[i]==1:
			FSK=np.concatenate((FSK,s1))
		else:
			FSK=np.concatenate((FSK,s0))
	return FSK

def createChirp(rate,chirp_len,chunk,begin_freq,end_freq):
	time_base=np.arange(0,chirp_len,1.0/rate)
	chirp_data_Hex=10*'\x00\x00' # add some zeros before the signal, this must be counted for the time of flight
	for t in np.nditer(time_base):
		chirp_data_Hex=chirp_data_Hex+struct.pack('h',int(scipy.signal.chirp(t,begin_freq,chirp_len,end_freq)*(32767))) #32767 is the max value for format paInt16
	chirp_data_Int=np.array(struct.unpack("%dh" % (len(chirp_data_Hex)/2), chirp_data_Hex))
	norm_chirp=math.sqrt(((chirp_data_Int/10000.0)*(chirp_data_Int/10000.0)).sum())*10000
	return chirp_data_Hex,chirp_data_Int,norm_chirp

def callback(in_data, frame_count, time_info, status):
	global call_chirp,call_flag,call_input,sema,nbrCall
	data=''
	if call_flag:
		flag=pyaudio.paContinue
	else:
		flag=pyaudio.paComplete
	if len(call_chirp)>2*frame_count:
		data=call_chirp[0:frame_count*2]
		call_chirp=call_chirp[frame_count*2:]
	else :
		data=data+frame_count*'\x00\x00'
	call_input[nbrCall*frame_count:(nbrCall+1)*frame_count]=np.array(struct.unpack("%dh" % (frame_count), in_data))

	nbrCall=nbrCall+1
	sema=sema+frame_count
	return (data, flag)
	
def  chirpDetection(chirp_data_int,norm_chirp): 
	f=0
	global sema,call_input
	START_STREAM=time.time()
	time.sleep(chirp_len+1)
	chirp_nbrOfFrames=len(chirp_data_int)
	peak_1=0
	peak_2=10000000000
	while True:
		if sema>2*len(chirp_data_int):
			elem=call_input[f*chirp_nbrOfFrames:(f+2)*chirp_nbrOfFrames]
			
			b,a=scipy.signal.butter(5,1500/(44100/2.0),btype='high')
			elem1=scipy.signal.lfilter(b,a,elem)
			norm_elem=math.sqrt(((elem1/100.0)*(elem1/100.0)).sum())*100
			conv=scipy.signal.fftconvolve(elem1,chirp_data_int[::-1],'valid')/(norm_elem*norm_chirp)
			conv_env=conv[scipy.signal.argrelmax(conv,order=10)]
			sema=sema-len(chirp_data_int)
			f=f+1
			
			if  max(conv_env)>0.2:  #freq_test  orand (sum(conv_env[peak_env-5:peak_env+5]>0.5*max(conv_env))<2)
				if peak_1==0:
					peak_1=f*chirp_nbrOfFrames+np.argmax(conv)
					print "PEAK 1 "+str(peak_1)
				else:
					peak_2=f*chirp_nbrOfFrames+np.argmax(conv)
					print "PEAK 2 "+str(peak_2)
					break
		if time.time()-START_STREAM>22:
			print "Real ending"	
			call_flag=False
			break	

	return peak_2-peak_1
########################################################################

# Define stream config
RATE = 44100
CHANNELS = 1
FORMAT = pyaudio.paInt16
chirp_len=0.2
begin_freq=3000
end_freq=6000
CHUNK = 32 #previously 128

#Valeur global

global call_chirp,call_flag,call_input,sema,nbrCall
call_flag=True
call_input=np.zeros(RATE*22) #call_input de 4 seconde permet de ne pas agrandir l'espace memoire pdt le callback
sema=0
nbrCall=0

# Define Frequency
fe = 44100
f0=2000
f1=4000
dt =1.0/fe
duration = 0.008
time_base=np.arange(0, duration, dt)

# Time
start_mod = time.time()

# Built reference sinus
s0 = generate_sin(time_base, f0)
s1 = generate_sin(time_base, f1)

# Built bip
fbip = 8000
tbip = np.arange(0, 0.1, dt)
bip = generate_sin(tbip, fbip)
bip_str = ''
for k in bip:
	bip_str = bip_str + struct.pack('h',int(k*(32767)))

# Config SRC & DST
if len(sys.argv) < 2:
	print("No dest id. (int) \n")
	sys.exit(-1)
id_dest = int(sys.argv[1])
id_source = 1

# Message to transmit
if len(sys.argv) < 3:
	print("No message to transmit (str) \n")
	magic_word = ''
	chirp_data_Hex,chirp_data_Int,norm_chirp=createChirp(RATE,chirp_len,CHUNK,begin_freq,end_freq)
	call_chirp=chirp_data_Hex
else:
	magic_word = sys.argv[2]

my_data = bits_convert_v2.tobits(magic_word)



# Built header
my_header = header_v3.toheader(id_source,id_dest,len(my_data)/8)

my_data_h = my_header + my_data

# Add protection
my_data_c = my_data_h + [0,0,0] 
n = 3
my_data_c = channel_coding(my_data_c,n)

# FSK modulation
my_fsk = fsk_modulation(my_data_c, s1, s0)

# To string
output_str = ''
for k in my_fsk:
	output_str = output_str + struct.pack('h',int(k*(32767)))

# Time
end_mod = time.time()

# Instantiate PyAudio
p = pyaudio.PyAudio()

# Open stream
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)
stream.start_stream()
print "Stream Start"

# Read bip
data = bip_str
# Play stream 
stream.write(data)
time.sleep(0.3)
# Read data
data = output_str
# Play stream 
stream.write(data)

if len(my_data)==0:
	data = chirp_data_Hex
	time.sleep(2.5)
	#stream.write(data) # Placer la fonction emetor 3 a cette endroit. 
	stream_c = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,output=True,input=True,frames_per_buffer=CHUNK,stream_callback=callback)
	stream_c.start_stream()
	print "Start Stream"
	PEAK=chirpDetection(chirp_data_Int,norm_chirp)-44100
	print "Nombre de frame de delay : "+str(PEAK) #88200 c'est le decalage inscrit dans receptor
	print "Distance en metre :"+str(330.0*PEAK/(2*RATE))	
	stream.stop_stream()
	stream.close()

# Stop stream
stream.stop_stream()
stream.close()

# Close PyAudio
p.terminate()
print "Stream End"

# Print info
print 'Time for modulation   (s):',end_mod - start_mod
print 'Time for transmission (s):',dt*len(my_fsk)
# print 'Time for transmission (s):',(len(my_data) + 20 +1)*n*duration
print 'Number of bit transmit   :',len(my_fsk)/len(time_base)
