'''
Autor : Simon
Date  : 23.07.2014
Title : receiver-bip.py
Resume: Decode a acoustic message in real time (require a bip)
'''

#import matplotlib.pyplot as plt
import scipy.fftpack as ff
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

def decode_fsk(signal, nb_echantillon):
	rest = len(signal) % nb_echantillon
	zero = np.zeros((nb_echantillon - rest))
	signal = np.concatenate((signal,zero))
	nb_trame = len(signal)/nb_echantillon
	signal_matrix = signal.reshape(nb_trame,nb_echantillon)
	message_rcv=[]
	for i in range(nb_trame):
		tmp=signal_matrix[i]
		if np.mean(tmp)>0.2:
			message_rcv.append(0)
		else:
			message_rcv.append(1)
	return message_rcv


def channel_decoding(message_rcv,n):
	message_bin=[]
	nb_trame = len(message_rcv)/n
	for i in range(nb_trame):
		tmp=message_rcv[i*n:(i+1)*n]
		if np.mean(tmp)<0.4:
			message_bin.append(0)
		else:
			message_bin.append(1)
	return message_bin
	
def find_sync(data_array, id_dest):
	# Filter
	N = 3
	Wn=(0.08,0.1)
	b, a = scipy.signal.butter(N, Wn, 'bandpass')
	data_filt = scipy.signal.filtfilt(b, a, data_array)
	# Absolute value
	my_signal_abs = abs(data_filt)
	my_signal_abs = my_signal_abs / max(my_signal_abs)
	# Detect first bit
	for k in range(len(my_signal_abs)):
		if my_signal_abs[k] > 0.2:
			my_signal_k = my_signal_abs[k:]
			break
	my_message_rcv = decode_fsk(my_signal_k, int(44100*0.008))
	# Channel decoding
	my_message_rcv = channel_decoding(my_message_rcv,3)
	# Extract the header
	sync,src,dst,len_data,shift = header_v3.fromheader(my_message_rcv, id_dest)
	if sync == None:
		my_str = None
	elif dst != id_dest:
		my_str = None
	else:
		# Isole the message
		data_to_decode = my_message_rcv[20+shift : 20+shift+len_data*8]
		# Message decode
		my_str=bits_convert_v2.frombits(data_to_decode)
	print 'Name of source            :',src
	print 'Name of dest              :',dst
	print 'Size of data              :',len_data
	print 'The magic word is         :',my_str
	return len_data

def createChirp(rate,chirp_len,chunk,begin_freq,end_freq):
	time_base=np.arange(0,chirp_len,1.0/rate)
	chirp_data_Hex=10*'\x00\x00' # add some zeros before the signal, this must be counted for the time of flight
	for t in np.nditer(time_base):
		chirp_data_Hex=chirp_data_Hex+struct.pack('h',int(scipy.signal.chirp(t,begin_freq,chirp_len,end_freq)*(32767))) #32767 is the max value for format paInt16
	chirp_data_Int=np.array(struct.unpack("%dh" % (len(chirp_data_Hex)/2), chirp_data_Hex))
	norm_chirp=math.sqrt(((chirp_data_Int/10000.0)*(chirp_data_Int/10000.0)).sum())*10000
	return chirp_data_Hex,chirp_data_Int,norm_chirp

def callback(in_data, frame_count, time_info, status):     #renvoi un chirp une demi seconde apres l'avoir recu (22050 echantillon)
	global call_chirp,call_flag,call_input,sema,nbrCall,PEAK,PEAK_FLAG,AUTOCAL
	data=''
	if call_flag:
		flag=pyaudio.paContinue
	else:	
		print "ERROR"
		flag=pyaudio.paComplete
	if nbrCall*frame_count>PEAK+44100-AUTOCAL: #and PEAK<(nbrCall+1)*frame_count+441000:
		PEAK_FLAG=True
		#data=(PEAK-nbrCall*frame_count+44100)*'\x00\x00'+call_chirp[0:frame_count*2-(PEAK-nbrCall*frame_count+44100)]
		#call_chirp=call_chirp[frame_count*2-(PEAK-nbrCall*frame_count+44100):]
	
	else :
		data=data+frame_count*'\x00\x00'
		if len(call_input[nbrCall*frame_count:(nbrCall+1)*frame_count])==len(np.array(struct.unpack("%dh" % (frame_count), in_data))):
			call_input[nbrCall*frame_count:(nbrCall+1)*frame_count]=np.array(struct.unpack("%dh" % (frame_count), in_data))
	if PEAK_FLAG:	
		data=call_chirp[0:frame_count*2]
		call_chirp=call_chirp[frame_count*2:]

	nbrCall=nbrCall+1
	sema=sema+frame_count
	return (data, flag)


def  chirpDetection(chirp_data_int,norm_chirp): 
	f=0
	global sema,call_input
	START_STREAM=time.time()
	time.sleep(1)
	chirp_nbrOfFrames=len(chirp_data_int)
	while True:
		if sema>2*len(chirp_data_int):
			elem=call_input[f*chirp_nbrOfFrames:(f+2)*chirp_nbrOfFrames]
			b,a=scipy.signal.butter(5,1500/(44100/2.0),btype='high')
			elem1=scipy.signal.lfilter(b,a,elem)
			norm_elem=math.sqrt(((elem1/100.0)*(elem1/100.0)).sum())*100
			conv=scipy.signal.fftconvolve(elem1,chirp_data_int[::-1],'valid')/((norm_elem)*norm_chirp)
			conv_env=conv[scipy.signal.argrelmax(conv,order=10)]
			#peak_env=np.argmax(conv_env)
			sema=sema-len(chirp_data_int)
			f=f+1
			# Controle frequentiel
#			felem=ff.rfft(elem1,44100)
#			cfchirp=np.zeros(len(felem)/2-1)
#			for i in range(len(felem)/2-1):
#				cfchirp[i]=abs(complex(felem[2*i+1],felem[2*i+2]))
#			cfchirp[0:100]=np.zeros(100)
#			freq_test=False
#			tiers1=np.mean(cfchirp[3000:4000])
#			tiers2=np.mean(cfchirp[4000:5000])
#			tiers3=np.mean(cfchirp[5000:6000])
#			if tiers2>tiers1*0.85 and tiers2<tiers1 and tiers3>tiers1*0.50 and tiers3<tiers1*0.65:
#				freq_test=True
#				print "FREQ OK"
#			print max(conv_env)
			if  max(conv_env)>0.4:  #freq_test or and (sum(conv_env[peak_env-5:peak_env+5]>0.5*max(conv_env))<2)
				peak=f*chirp_nbrOfFrames+np.argmax(conv)
				print "OK"
				break

		if time.time()-START_STREAM>20:
			print "Real ending"	
			call_flag=False
			break
	return peak

########################################################################

# Define stream config
WIDTH = 2
CHANNELS = 1
RATE = 44100
FORMAT = pyaudio.paInt16
CHUNK = 1024
RECORD_SECONDS = 2

# Define Frequency
fe = 44100
f0=2000
f1=4000
dt =1.0/fe
duration = 0.008
time_base=np.arange(0, duration, dt)

# Define chirp
chirp_len=0.2
begin_freq=3000
end_freq=6000
CHUNK_c = 32 #previously 128
global call_chirp,call_flag,call_input,sema,nbrCall,PEAK,PEAK_FLAG,AUTOCAL
AUTOCAL=14100 #a definir a l'aide de la fonction d'autocalibration
PEAK=1000000000
PEAK_FLAG=False
call_flag=True
call_input=np.zeros(RATE*22) #call_input de 4 seconde permet de ne pas agrandir l'espace memoire pdt le callback
sema=0
nbrCall=0
chirp_data_Hex,chirp_data_Int,norm_chirp=createChirp(RATE,chirp_len,CHUNK,begin_freq,end_freq)
call_chirp=chirp_data_Hex
print "Chirp created"


# Config DST
id_dest = 2
micro_input = ''
start = time.time()

# Filter 8kHz
N = 3
Wn=(0.35,0.38)
b8, a8 = scipy.signal.butter(N, Wn, 'bandpass')

# Instantiate PyAudio
p = pyaudio.PyAudio()

# Open stream
print "Stream Start"
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Record micro
while (time.time()-start) < 40:
	for i in range(5):
		data = stream.read(CHUNK)
		micro_input = micro_input + data
	# filter 8kHz
	frames = len(micro_input)/2 
	data_array = np.array(struct.unpack("%dh" % (frames), micro_input))
	data_array = data_array / max(abs(data_array))
	data_filt = scipy.signal.filtfilt(b8, a8, data_array)
	micro_input=''
	if max(data_filt) > 0.4:
		print max(data_filt)
		for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
			data = stream.read(CHUNK)
			micro_input = micro_input + data
		# Convert micro(str) to array
		frames = len(micro_input)/2 
		data_array = np.array(struct.unpack("%dh" % (frames), micro_input))
		chirp = find_sync(data_array, id_dest)
		micro_input=''
		if chirp == 0:
			# Run chirp test
			print 'ready'
			stream_c = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,output=True,input=True,frames_per_buffer=CHUNK_c,stream_callback=callback)
			stream_c.start_stream()
			print "Start Stream"
			PEAK=chirpDetection(chirp_data_Int,norm_chirp)
			print "Detection du PEAK a : "+str(PEAK)
			while stream_c.is_active():
				time.sleep(0.1)
			stream_c.stop_stream()
			stream_c.close()


# Stop stream
stream.stop_stream()
stream.close()

# Close PyAudio
p.terminate()
print "Stream End"

'''
#data_fft=np.fft.fft(data_filt,44100)
#my_signal = abs(data_fft[100:44000])

plt.plot(data_filt)
plt.axis('tight')
plt.show()
'''
