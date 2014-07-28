'''
Autor : Simon
Date  : 10.07.2014
Title : bits_convert_v2.py
Resume: Convert string to list of bits / list of bits to string
		Convert dec to list of bits / list of bits to dec
'''

def tobits(s):
    result = []
    for c in s:
        bits = bin(ord(c))[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result
  
    
def frombits(bits):
    chars = []
    for b in range(len(bits) / 8):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)
    

def dec_to_bin(x,n):
	x=x%(2**n)
	y = bin(x)
	z = list(y)
	result=z[2:]
	for i in range(len(result)):
		result[i]=int(result[i])
	while len(result) < n:
		result=[0]+result
	return result


def bin_to_dec(liste):
	n = len(liste)
	x = 0
	for i in range(n):
		x = x + liste[i]*(2**(n-i-1))
	return x

########################################################################

if __name__ == '__main__':
	print tobits('Hello')
	print frombits([0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 
	1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1])
	print frombits([0, 1, 1, 0, 0, 0, 0, 1, 1])
	print tobits('a')
	print bin_to_dec([1,1,1,1,1,1,1,1])
	print dec_to_bin(255,8)
	print dec_to_bin(2,4)
	print tobits('')

