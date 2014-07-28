'''
Autor : Simon
Date  : 21.07.2014
Title : header_v3.py
Resume: Create the header for acoustic channel
		Decode the header and check for control data
'''
import bits_convert_v2 as b

########################################################################

# sync = 15				- 8 bits
# id. src = ?			- 4 bits
# id. dst = ?			- 4 bits
# len_data = ? in bytes - 4 bits


def toheader(source, dest, l_data):
    sync = b.dec_to_bin(15,8)							# sync
    src = b.dec_to_bin(source,4)
    dst = b.dec_to_bin(dest,4)
    len_data= b.dec_to_bin(l_data,4)
    header = sync + src + dst + len_data
    return header


def fromheader(data, desti):
	# i is the shift
	i=0
	if len(data) > 19:
		# Decode sync
		sync = b.bin_to_dec(data[i:i+8])
		while sync != 15:											# sync
			i=i+1
			sync = b.bin_to_dec(data[i:i+8])
			if len(data[i:])<20:
				return None, None, None, None, None
		dst = b.bin_to_dec(data[i+12:i+16])
		if dst == desti:
			src = b.bin_to_dec(data[i+8:i+12])
			len_data = b.bin_to_dec(data[i+16:i+20])
			return sync, src, dst, len_data, i
		elif b.bin_to_dec(data[i+13:i+1+17]) == desti:
			i=i+1
			dst = b.bin_to_dec(data[i+12:i+16])
			src = b.bin_to_dec(data[i+8:i+12])
			len_data = b.bin_to_dec(data[i+16:i+20])
			return sync, src, dst, len_data, i
		else:
			return sync, None, 'You are not dest', None, None
	else:
		return None, None, None, None, None
		


########################################################################

if __name__ == '__main__':
	print toheader(0,2,1)
	print toheader(15,0,2)
	print fromheader([0,0,0], 3)
	a = toheader(0,2,1)
	print a
	print fromheader(a, 0)
	print fromheader(a, 2)
	a = [0,0,0] + a + [0,0,0]
	print fromheader(a, 2)

	

