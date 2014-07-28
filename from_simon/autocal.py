import numpy as np
import time
import pyaudio
import struct
import scipy.signal as ss
import math


def createChirp(rate,chirp_len,chunk,begin_freq,end_freq):
	time_base=np.arange(0,chirp_len,1.0/rate)
	chirp_data_Hex=10*'\x00\x00' # add some zeros before the signal, this must be counted for the time of flight
	for t in np.nditer(time_base):
		chirp_data_Hex=chirp_data_Hex+struct.pack('h',int(ss.chirp(t,begin_freq,chirp_len,end_freq)*(32767))) #32767 is the max value for format paInt16
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
	START_STREAM=time.time()
	time.sleep(chirp_len+0.3)
	chirp_nbrOfFrames=len(chirp_data_int)
	while True:
		if sema>2*len(chirp_data_int):
			elem=call_input[f*chirp_nbrOfFrames:(f+2)*chirp_nbrOfFrames]	
			norm_elem=math.sqrt(((elem/100.0)*(elem/100.0)).sum())*100
			conv=ss.fftconvolve(elem,chirp_data_int[::-1],'valid')/((norm_elem)*norm_chirp)
			conv_env=conv[ss.argrelmax(conv,order=30)]
			peak_env=np.argmax(conv_env)
			f=f+1
			if sum(conv_env[peak_env-10:peak_env+10]>0.3*max(conv_env))<2:
				peak=f*chirp_nbrOfFrames+np.argmax(conv)
				break
		if time.time()-START_STREAM>5:
			print "Real ending"	
			call_flag=False
			break
	return peak

if __name__=='__main__':
	chirp_len=0.2
	RATE=44100
	begin_freq=3000
	end_freq=6000
	CHANNELS = 1
	
	CHUNK = 32 #previously 128
	FORMAT = pyaudio.paInt16 #previously paInt16
	#Variables inside callback must be global
	global call_chirp,call_flag,call_input,sema,nbrCall
	call_flag=True
	call_input=np.zeros(RATE*4) #call_input de 4 seconde permet de ne pas agrandir l'espace memoire pdt le callback
	sema=0
	nbrCall=0
	p = pyaudio.PyAudio()
	chirp_data_Hex,chirp_data_Int,norm_chirp=createChirp(RATE,chirp_len,CHUNK,begin_freq,end_freq)
	call_chirp=chirp_data_Hex

	stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,output=True,input=True,frames_per_buffer=CHUNK,stream_callback=callback)
	stream.start_stream()
	print "Start Stream"
	print "Nombre de frame de retard : "+str(chirpDetection(chirp_data_Int,norm_chirp))
	stream.stop_stream()
	stream.close()
	p.terminate()

