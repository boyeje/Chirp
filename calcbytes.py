def hextobitsBE ( str_hex):        # return a list of 8bits Big-Endian from an hex number (in a string)
	h=int(ord(str_hex))
	bits=[0,0,0,0,0,0,0,0]
	for i in range(8):
		bits[i]=h%2
		h=h/2
	return bits

def hexhextobitsBE(str_hexdouble): # return a list of 16bits Big-Endian from two hex number (in a string)
	if len(str_hexdouble)==1:
		return hextobitsBE ( str_hexdouble)
	elif len(str_hexdouble)==0:
		return [0]
	else:
		return hextobitsBE(str_hexdouble[0])+hextobitsBE(str_hexdouble[1])

def bitstointBE( bitstab): # toujours en big-endian
	num=0
	bits=bitstab[-1:-(len(bitstab)+1):-1]
	j=0
	for i in bits:
		if i==1:
			num=num+2**j
		j=j+1
	return num

def hextobitsLE ( str_hex):        # return a list of 8bits Little-Endian from an hex number (in a string)
	h=int(ord(str_hex))
	bits=[0,0,0,0,0,0,0,0]
	for i in range(8):
		bits[-(i+1)]=h%2
		h=h/2
	return bits

def hexhextobitsLE(str_hexdouble): # return a list of 16bits Little-Endian from two hex number (in a string)
	if len(str_hexdouble)==1:
		return hextobitsLE ( str_hexdouble)
	elif len(str_hexdouble)==0:
		return [0]
	else:
		return hextobitsLE(str_hexdouble[1])+hextobitsLE(str_hexdouble[0])

def bitstointLE( bitstab): # toujours en Little-endian
	num=0
	j=0
	for i in bitstab:
		if i==1:
			num=num+2**j
		j=j+1
	return num
