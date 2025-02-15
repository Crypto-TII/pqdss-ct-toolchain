def xor(bytestr1, bytestr2):
    """ Return the XOR operation between the two inputs """
    return bytes(a ^ b for a, b in zip(bytestr1, bytestr2))

def map_to_bits(idx, bytestr_size):
    """ Return a lambda-bit bytestring that
        represend the input index in little endian
    """
    return idx.to_bytes(bytestr_size, byteorder='little')

def split_in_two(data, bytesize):
    """ Split the input data into two consecutive chunks, where the first chunk is of the given size """
    return data[:bytesize], data[bytesize:]
    
def pad_left(bytestr, padding_bytesize):
    """ Pad a bytestring with zeroes on the left """
    return bytes([0]*padding_bytesize) + bytestr

def bytestring_to_bitstring(bytestr):
    """ Convert a bytestring into a bitstring """
    bitstr = ''
    for y in bytestr:
        bitstr += bin(y)[2:].rjust(8, '0')[::-1]
    return bitstr

def bitstring_to_bytestring(bitstr):
    """ Convert a bitstring into a bytestring """
    assert len(bitstr) % 8 == 0
    return bytes([
        int(bitstr[i*8:(i+1)*8][::-1], base=2)
        for i in range(len(bitstr)//8)
    ])

def bitstring_to_integer(bitstr):
    """ Convert a bitstring into an integer """
    return int(bitstr[::-1], base=2)

def truncate_bits_and_pad(bytestr, truncation_limit, padded_str_bitsize):
    """ Truncate a bytestring to keep only the first 'truncation_limit' bits
        and pad with zeroes on the right to have a bytestring that
        contains 'padded_str_bitsize' bits
    """
    assert padded_str_bitsize % 8 == 0
    bitstr = bytestring_to_bitstring(bytestr)    
    bitstr = bitstr[:truncation_limit].ljust(padded_str_bitsize, '0')
    return bitstring_to_bytestring(bitstr)
