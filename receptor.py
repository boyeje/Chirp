import numpy as np
import time
import pyaudio
import struct
import scipy.signal as ss
import math
import scipy.fftpack as ff

def createChirp(rate,chirp_len,chunk,begin_freq,end_freq):
	time_base=np.arange(0,chirp_len,1.0/rate)
	chirp_data_Hex=10*'\x00\x00' # add some zeros before the signal, this must be counted for the time of flight
	for t in np.nditer(time_base):
		chirp_data_Hex=chirp_data_Hex+struct.pack('h',int(ss.chirp(t,begin_freq,chirp_len,end_freq)*(32767))) #32767 is the max value for format paInt16
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
			b,a=ss.butter(5,1500/(44100/2.0),btype='high')
			elem1=ss.lfilter(b,a,elem)
			norm_elem=math.sqrt(((elem1/100.0)*(elem1/100.0)).sum())*100
			conv=ss.fftconvolve(elem1,chirp_data_int[::-1],'valid')/((norm_elem)*norm_chirp)
			conv_env=conv[ss.argrelmax(conv,order=10)]
			#peak_env=np.argmax(conv_env)
			sema=sema-len(chirp_data_int)
			f=f+1
			# Controle frequentiel
			felem=ff.rfft(elem1,44100)
			cfchirp=np.zeros(len(felem)/2-1)
			for i in range(len(felem)/2-1):
				cfchirp[i]=abs(complex(felem[2*i+1],felem[2*i+2]))
			cfchirp[0:100]=np.zeros(100)
			freq_test=False
			tiers1=np.mean(cfchirp[3000:4000])
			tiers2=np.mean(cfchirp[4000:5000])
			tiers3=np.mean(cfchirp[5000:6000])
			if tiers2>tiers1*0.85 and tiers2<tiers1 and tiers3>tiers1*0.50 and tiers3<tiers1*0.65:
				freq_test=True
				print "FREQ OK"
			print max(conv_env)
			if  max(conv_env)>0.2:  #freq_test or and (sum(conv_env[peak_env-5:peak_env+5]>0.5*max(conv_env))<2)
				peak=f*chirp_nbrOfFrames+np.argmax(conv)
				print "OK"
				break

		if time.time()-START_STREAM>20:
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

	CHUNK = 16 #previously 128
	FORMAT = pyaudio.paInt16 #previously paInt16
	#Variables inside callback must be global
	global call_chirp,call_flag,call_input,sema,nbrCall,PEAK,PEAK_FLAG,AUTOCAL
	AUTOCAL=14250 #a definir a l'aide de la fonction d'autocalibration
	PEAK=1000000000
	PEAK_FLAG=False
	call_flag=True
	call_input=np.zeros(RATE*22) #call_input de 4 seconde permet de ne pas agrandir l'espace memoire pdt le callback
	sema=0
	nbrCall=0
	p = pyaudio.PyAudio()
	chirp_data_Hex,chirp_data_Int,norm_chirp=createChirp(RATE,chirp_len,CHUNK,begin_freq,end_freq)
	call_chirp=chirp_data_Hex
	print "Chirp created"

	stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,output=True,input=True,frames_per_buffer=CHUNK,stream_callback=callback)
	stream.start_stream()
	print "Start Stream"
	
	PEAK=chirpDetection(chirp_data_Int,norm_chirp)
	print "Detection du PEAK a : "+str(PEAK)

	while stream.is_active():
		time.sleep(0.1)


	stream.stop_stream()
	stream.close()
	p.terminate()
