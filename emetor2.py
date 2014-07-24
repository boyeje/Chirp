import numpy as np
import time
import pyaudio
import struct
import time
import scipy.signal as ss
import scipy.fftpack as ff
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
	global call_chirp,call_flag,call_input,sema,nbrCall  #chirp data, bolean (true to continue),input microphone,semaphor (used to control access to call_input)
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
	
def  chirpDetection(chirp_data,rate,START_STREAM): 
	global call_input,sema,call_flag
	print "DETECTION"
	time.sleep(chirp_len+0.5) #wait for the end of emission (better sound)
	chirp_nbrOfFrames=len(chirp_data)/2
	chirp_array=np.array(struct.unpack("%dh" % (chirp_nbrOfFrames), chirp_data))
	norm_chirp=math.sqrt(((chirp_array/10000.0)*(chirp_array/10000.0)).sum())*10000 #np.linalg.norm(chirp_array)
	f=0
	i=0
	bip_1=0
	bip_2=0
	#DO NOT FORGET THE SEMAPHORE
	convPlot=np.array([])
	convPlot2=np.array([])
	while True:
		
		if sema>2*chirp_nbrOfFrames:
			#correlation sur la longueur de 2 chirp
			elem=call_input[f*chirp_nbrOfFrames:(f+2)*chirp_nbrOfFrames]
			f=f+1
			norm_elem=math.sqrt(((elem/100.0)*(elem/100.0)).sum())*100 #np.linalg.norm(elem)+1 #math.sqrt((elem*elem).sum())
			#norm_elem=np.zeros(len(elem)-len(chirp_array)+1)
			#start =time.time()
			#for y in range(len(elem)-len(chirp_array)+1):
				#norm_elem[y]=math.sqrt(((elem[y:y+len(chirp_array)]/10.0)**2).sum())*10.0
				#norm_elem[y]= np.linalg.norm(elem[y:y+len(chirp_array)])
			#print "Duree calcul nouvelle norme   "+str(time.time()-start)	
			#start_detect2=time.time()
			#print "Norme du elem    "+str(norm_elem)
			#corr=np.correlate(elem,chirp_array)/(norm_chirp*norm_elem+1)
			corr=0
			i=i+1
			
			#conv2=ss.fftconvolve(elem,chirp_array[::-1],'valid')/(norm_elem2*norm_chirp)
			#convPlot=np.concatenate((convPlot,conv))
			b,a=ss.butter(10,1500/(44100/2.0),btype='high')
			elem1=ss.lfilter(b,a,elem)
			#b,a=ss.butter(5,20000/(44100/2.0),btype='low')
			#elem2=ss.lfilter(b,a,elem1)
			conv=ss.fftconvolve(elem1,chirp_array[::-1],'valid')/(norm_elem*norm_chirp)
			conv2=ss.fftconvolve(elem,chirp_array[::-1],'valid')/(norm_elem*norm_chirp)
			convPlot=np.concatenate((convPlot,conv))
			convPlot2=np.concatenate((convPlot,conv2))
			#print time.time()-start_detect2
			#print "Norme du chirp "+str(norm_chirp)
			#print "Norme du elem "+str(norm_elem)
			#print "Valeur correlation : "+str(max(corr))
			#print "Valeur convolution : "+str(max(conv))
			#print "Norme du son entrant : "+str(norm_elem)
			#print sema
			if False:#max(corr)>0.8:  #Value should be reconsidered
				if bip_1==0:
					bip_1=f+np.argmax(corr)
				else:
					bip_2=f+np.argmax(corr)
					call_flag=False
					break
			sema=sema-chirp_nbrOfFrames
			
		if time.time()-START_STREAM>3:
			print "Real ending"	
			call_flag=False
			break
	#Creation de plot
	#for p in range(3):
	#	print 3*100+10+p+1
		#plt.subplot(3*100+10+p+1)
		#plt.plot((convPlot[p*22050:(p+1)*22050]),'b')
		#plt.subplot(3*100+20+2*p+2)
		#plt.plot((convPlot2[2*p*2*chirp_nbrOfFrames:2*p*2*chirp_nbrOfFrames+2*chirp_nbrOfFrames]**2)[ss.argrelmax(convPlot2[2*p*2*chirp_nbrOfFrames:2*p*2*chirp_nbrOfFrames+2*chirp_nbrOfFrames]**2,order=20)],'r')
		#plt.plot((convPlot[p*2*chirp_nbrOfFrames:p*2*chirp_nbrOfFrames+2*chirp_nbrOfFrames]))
	#plt.plot(convPlot[0:22050])
	plt.subplot(211)
	plt.plot(convPlot2[5000:8000])
	plt.subplot(212)
	plt.plot(convPlot[5000:8000])
	plt.show()
	return 1.0*(bip_2-bip_1)/rate
	
	
if __name__ == '__main__':
	chirp_len=0.2
	RATE=44100
	begin_freq=3000
	end_freq=6000
	CHANNELS = 1
	
	CHUNK = 128 #previously 1024
	FORMAT = pyaudio.paInt16 #previously paInt16
	#Variables inside callback must be global
	global call_chirp,call_flag,call_input,sema,nbrCall
	call_flag=True
	call_input=np.zeros(RATE*4) #call_input de 6 seconde permet de ne pas agrandir l'espace memoire pdt le callback
	sema=0
	nbrCall=0
	p = pyaudio.PyAudio()
	chirp_data=createChirp(RATE,chirp_len,CHUNK,begin_freq,end_freq)
	call_chirp=chirp_data
	
	stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,output=True,input=True,frames_per_buffer=CHUNK,stream_callback=callback)
	
	stream.start_stream()
	print "Start Stream"
	timme=chirpDetection(chirp_data,RATE,time.time())
	call_flag=False
	
	while stream.is_active():
		time.sleep(0.1)
	stream.stop_stream()
	stream.close()
	#start=time.time()
	chirp_array=np.array(struct.unpack("%dh" % (len(chirp_data)/2), chirp_data))
	#print np.linalg.norm(bigarray)
	norm_chirp=math.sqrt(((chirp_array/10000.0)*(chirp_array/10000.0)).sum())*10000
	norm_callinput=math.sqrt(((call_input/10000.0)*(call_input/10000.0)).sum())*10000
	#print norm_callinput
	#norm_chirp=np.linalg.norm(chirp_array)
	#corr=np.correlate(bigarray,chirp_array)
	conv=ss.fftconvolve(call_input,chirp_array[::-1],'same')/(norm_chirp*norm_callinput)
	#print time.time()-start 
	conv_env=conv[ss.argrelmax(conv,order=30)]
	plt.plot(conv_env)
	plt.show()
 	
	p.terminate()
	
