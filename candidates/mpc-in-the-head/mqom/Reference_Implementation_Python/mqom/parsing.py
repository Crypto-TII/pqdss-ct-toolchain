from .bits import bytestring_to_bitstring, bitstring_to_bytestring
from .field import BinaryField

class ParsingFormat:
    def get_bytesize(self):
        raise NotImplementedError()
    
    def parse(self, bytestr):
        raise NotImplementedError()
    
class ByteStrFrmt(ParsingFormat):
    def __init__(self, byte_size):
        self._byte_size = byte_size

    def get_bytesize(self):
        return self._byte_size
    
    def parse(self, bytestr):
        assert len(bytestr) == self._byte_size
        return bytestr
    
class VectorFrmt(ParsingFormat):
    def __init__(self, field, length):
        assert issubclass(field, BinaryField)
        self._field = field
        self._length = length

    def get_bytesize(self):
        return (self._length * self._field.bitsize + 7) // 8
    
    def parse(self, bytestr):
        assert len(bytestr) == self.get_bytesize()
        bitstr = bytestring_to_bitstring(bytestr)
        vec = [
            self._field.from_bitstring(
                bitstr[i*self._field.bitsize:(i+1)*self._field.bitsize]
            ) for i in range(self._length)
        ]
        assert bitstr[self._length * self._field.bitsize:] == '0'*(self.get_bytesize()-self._length * self._field.bitsize)
        return vec
    
    @classmethod
    def serialize(cls, vec):
        bitstring = ''
        for v in vec:
            assert isinstance(v, BinaryField)
            bitstring += v.to_bitstring()
        return bitstring_to_bytestring(bitstring)

class MatrixFrmt(ParsingFormat): # Line-wise
    def __init__(self, field, nb_rows, nb_cols):
        self.row_format = VectorFrmt(field, nb_cols)
        self.nb_rows = nb_rows

    def get_bytesize(self):
        row_byte_size = self.row_format.get_bytesize()
        return row_byte_size*self.nb_rows
    
    def parse(self, bytestr):
        row_byte_size = self.row_format.get_bytesize()
        return [
            self.row_format.parse(
                bytestr[num_row*row_byte_size:(num_row+1)*row_byte_size]
            ) for num_row in range(self.nb_rows)
        ]

class ArrayFrmt(ParsingFormat):
    def __init__(self, *args):
        for arg in args:
            assert isinstance(arg, ParsingFormat)
        self.args = args

    def get_bytesize(self):
        byte_size  = 0
        for arg in self.args:
            byte_size += arg.get_bytesize()
        return byte_size

    def parse(self, bytestr):
        data = []
        for arg in self.args:
            byte_size = arg.get_bytesize()
            ser_data, bytestr = bytestr[:byte_size], bytestr[byte_size:]
            data.append(arg.parse(ser_data))
        return data

def parse(bytestr, *args):
    data = []
    for arg in args:
        assert isinstance(arg, ParsingFormat)
        byte_size = arg.get_bytesize()
        ser_data, bytestr = bytestr[:byte_size], bytestr[byte_size:]
        data.append(arg.parse(ser_data))
    return data

def serialize(*args):
    data = b''
    for arg in args:
        if type(arg) in [list, tuple]:
            if type(arg[0]) not in [bytes, list, tuple]:
                data += VectorFrmt.serialize(arg)
                continue
            data += serialize(*arg)
        
        elif type(arg) == bytes:
            data += arg

        else:
            raise TypeError(type(arg))
        
    return data


def expand_seed(prg, seed, *args):
    tot_byte_size = 0
    for arg in args:
        assert isinstance(arg, ParsingFormat)
        tot_byte_size += arg.get_bytesize()

    if seed is None:
        expanded_bytestring = prg(None, tot_byte_size)
    else:
        expanded_bytestring =  prg(b'\x00'*len(seed), 0, seed, tot_byte_size)
    
    return parse(expanded_bytestring, *args)
