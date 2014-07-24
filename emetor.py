import numpy as np
import time
import pyaudio
import struct
import time
import scipy.signal as ss
import math
import matplotlib.pyplot as plt

def main():
	
	return 0

def createChirp(rate,chirp_len,chunk,begin_freq,end_freq):
	time_base=np.arange(0,chirp_len,1.0/rate)
	chirp_data=10*'\x00\x00' # add some zeros before the signal, this must be counted for the time of flight
	for t in np.nditer(time_base):
		chirp_data=chirp_data+struct.pack('h',int(ss.chirp(t,begin_freq,chirp_len,end_freq)*(32767))) #32767 is the max value for format paInt16
	return chirp_data
	
def autocalibration_1(stream,rate): # returns global latency in frames
	return int((stream.get_input_latency()+stream.get_output_latency())*rate)

def callback(in_data, frame_count, time_info, status):
	global call_chirp,call_flag,call_input,sema  #chirp data, bolean (true to continue),input microphone,semaphor (used to control access to call_input)
	data=''
	i=0
	if call_flag:
		flag=pyaudio.paContinue
	else:
		flag=pyaudio.paComplete
	if len(call_chirp)>2*frame_count:
		i=i+1
		data=call_chirp[0:frame_count*2]
		call_chirp=call_chirp[frame_count*2:]
	else :
		data=data+frame_count*'\x00\x00'
	call_input=call_input+in_data
	sema=sema+frame_count
	return (data, flag)
	
def  chirpDetection(chirp_data,rate,chirp_len): 
	global call_input,sema,call_flag
	time.sleep(chirp_len+1) #wait for the end of emission (better sound)
	chirp_nbrOfFrames=len(chirp_data)/2
	chirp_array=np.array(struct.unpack("%dh" % (chirp_nbrOfFrames), chirp_data))
	
	norm_chirp=math.sqrt(((chirp_array/10000.0)*(chirp_array/10000.0)).sum())*10000 #np.linalg.norm(chirp_array)
	
	f=0
	i=0
	bip_1=0
	bip_2=0
	#DO NOT FORGET THE SEMAPHORE
	start_detect=time.time()
	convPlot=np.array([])
	while True:
		if sema>2*chirp_nbrOfFrames:
			#correlation sur la longueur de 2 chirp
			elem=np.array(struct.unpack("%dh" % (2*chirp_nbrOfFrames), call_input[2*f:2*f+4*chirp_nbrOfFrames]))
			norm_elem=math.sqrt(((elem/10000.0)*(elem/10000.0)).sum())*10000 #np.linalg.norm(elem)+1 #math.sqrt((elem*elem).sum())
			start_detect2=time.time()
			#corr=np.correlate(elem,chirp_array)/(norm_chirp*norm_elem+1)
			corr=0
			i=i+1
			conv=ss.fftconvolve(elem,chirp_array[::-1],'full')/(norm_elem*norm_chirp)
			convPlot=np.concatenate((convPlot,conv))
			print time.time()-start_detect2
			#print "Norme du chirp "+str(norm_chirp)
			#print "Norme du elem "+str(norm_elem)
			#print "Valeur correlation : "+str(max(corr))
			print "Valeur convolution : "+str(max(conv))
			if False:#max(corr)>0.8:  #Value should be reconsidered
				if bip_1==0:
					bip_1=f+np.argmax(corr)
				else:
					bip_2=f+np.argmax(corr)
					call_flag=False
					break
			sema=sema-2*chirp_nbrOfFrames
			f=f+2*chirp_nbrOfFrames
		if time.time()-start_detect>2:
			print "Real ending"
			call_flag=False
			break
	#Creation de plot
	if i<10:
		for p in range(i):
			print i*100+10+p+1
			plt.subplot(i*100+10+p+1)
			plt.plot(convPlot[p*2*chirp_nbrOfFrames:p*2*chirp_nbrOfFrames+2*chirp_nbrOfFrames])
	else:
		for p in range(5):
			plt.subplot(9*100+10+p+1)
			plt.plot(convPlot[p*2*chirp_nbrOfFrames:p*2*chirp_nbrOfFrames+2*chirp_nbrOfFrames])	
	plt.show()
	return 1.0*(bip_2-bip_1)/rate
	
	
if __name__ == '__main__':
	chirp_len=0.5
	RATE=44100
	begin_freq=2000
	end_freq=8000
	CHANNELS = 1
	CHUNK = 1024 #previously 1024
	FORMAT = pyaudio.paInt16 #previously paInt16
	#Variables inside callback must be global
	global call_chirp,call_flag,call_input,sema
	call_flag=True
	call_input=''
	sema=0
	p = pyaudio.PyAudio()
	chirp_data=createChirp(RATE,chirp_len,CHUNK,begin_freq,end_freq)
	call_chirp=chirp_data
	
	stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,output=True,input=True,frames_per_buffer=CHUNK,stream_callback=callback)
	
	stream.start_stream()
	print "Start Stream"
	timme=chirpDetection(chirp_data,RATE,chirp_len)
	
	while stream.is_active():
		print "Stream finished"
		time.sleep(0.1)
		
	
	stream.stop_stream()
	stream.close()
	#start=time.time()
	bigarray=np.array((struct.unpack("%dh" % (len(call_input)/2), call_input)))
	chirp_array=np.array(struct.unpack("%dh" % (len(chirp_data)/2), chirp_data))
	#print np.linalg.norm(bigarray)
	norm_bigarray=math.sqrt(((bigarray/10000.0)*(bigarray/10000.0)).sum())*10000
	print norm_bigarray
	#norm_chirp=np.linalg.norm(chirp_array)
	#corr=np.correlate(bigarray,chirp_array)
	conv=ss.fftconvolve(bigarray,chirp_array[::-1])/(np.linalg.norm(chirp_array)*norm_bigarray)
	#print time.time()-start 
	#plt.plot(conv)
	#plt.show()
 
	p.terminate()
	
