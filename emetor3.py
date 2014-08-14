import numpy as np
import time
import pyaudio
import struct
import scipy.signal as ss
import math
import scipy.fftpack as ff
#import matplotlib.pyplot as plt

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
	global sema,call_input
	START_STREAM=time.time()
	time.sleep(chirp_len+1)
	chirp_nbrOfFrames=len(chirp_data_int)
	peak_1=0
	peak_2=10000000000
	convPlot=np.array([])
	while True:
		if sema>2*len(chirp_data_int):
			elem=call_input[f*chirp_nbrOfFrames:(f+2)*chirp_nbrOfFrames]
			
			b,a=ss.butter(5,1500/(44100/2.0),btype='high')
			elem1=ss.lfilter(b,a,elem)
			norm_elem=math.sqrt(((elem1/100.0)*(elem1/100.0)).sum())*100
			conv=ss.fftconvolve(elem1,chirp_data_int[::-1],'valid')/(norm_elem*norm_chirp)
			conv_env=conv[ss.argrelmax(conv,order=10)]
			peak_env=np.argmax(conv_env)
			sema=sema-len(chirp_data_int)
			f=f+1
			
			# Controle frequentiel
			#ret=time.time()
			felem=ff.rfft(elem1,44100)
			cfchirp=np.zeros(len(felem)/2-1)
			for i in range(len(felem)/2-1):
				cfchirp[i]=abs(complex(felem[2*i+1],felem[2*i+2]))
			cfchirp[0:100]=np.zeros(100)
			convPlot=np.concatenate((convPlot,cfchirp))
			freq_test=False
			tiers1=np.mean(cfchirp[3000:4000])
			tiers2=np.mean(cfchirp[4000:5000])
			tiers3=np.mean(cfchirp[5000:6000])
			#print tiers1
			#print tiers2
			#print tiers3
			if tiers2>tiers1*0.8 and tiers2<tiers1 and tiers3>tiers1*0.45 and tiers3<tiers1*0.65:
				freq_test=True
				print "TRUE"
				#print "OK"
				#print max(conv_env)
			#else:
				#print "No chirp here"
				#print max(conv_env)
			#print "Temps de calcul de fft et de son test  " + str(time.time()-ret)
			print max(conv_env)
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
#	for i in range(3):
#		plt.subplot(300+10+i)
#		plt.plot(convPlot[i*22050:(i+1)*22050])
#	plt.show()
	return peak_2-peak_1

if __name__=='__main__':
	chirp_len=0.2
	RATE=44100
	begin_freq=3000
	end_freq=6000
	CHANNELS = 1
	
	CHUNK = 16 #previously 128
	FORMAT = pyaudio.paInt16 #previously paInt16
	#Variables inside callback must be global
	global call_chirp,call_flag,call_input,sema,nbrCall
	call_flag=True
	call_input=np.zeros(RATE*22) #call_input de 4 seconde permet de ne pas agrandir l'espace memoire pdt le callback
	sema=0
	nbrCall=0
	p = pyaudio.PyAudio()
	chirp_data_Hex,chirp_data_Int,norm_chirp=createChirp(RATE,chirp_len,CHUNK,begin_freq,end_freq)
	call_chirp=chirp_data_Hex
	stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,output=True,input=True,frames_per_buffer=CHUNK,stream_callback=callback)
	stream.start_stream()
	print "Start Stream"
	PEAK=chirpDetection(chirp_data_Int,norm_chirp)-44100
	print "Nombre de frame de delay : "+str(PEAK) #88200 c'est le decalage inscrit dans receptor
	print "Distance en metre :"+str(330.0*PEAK/(2*RATE))	
	stream.stop_stream()
	stream.close()
	p.terminate()
