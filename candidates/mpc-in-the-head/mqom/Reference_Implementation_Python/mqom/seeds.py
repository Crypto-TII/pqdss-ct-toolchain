from .bits import xor, map_to_bits, split_in_two

def lin_ortho(bytestr):
    """ Linear orthomorphism """
    left, right = split_in_two(bytestr, len(bytestr)//2)
    return xor(left, right) + left

def tweak_salt(params, salt, sel, e, j):
    """ Return a tweak of the salt using the
        repetition index e and the tree depth j
    """
    return xor(
        salt,
        map_to_bits(sel + 4*e + 256*j, len(salt))
    )

def seed_derive(params, salt, seed):
    """ Derive the left child of a seed node """
    seed_ = lin_ortho(seed)
    return xor(params.enc(key=salt, ptx=seed), seed_)

def seed_commit(params, salt, seed):
    seed_ = lin_ortho(seed)
    com1 = xor(params.enc(key=salt, ptx=seed), seed_)
    com2 = xor(params.enc(key=xor(salt, map_to_bits(1, len(salt))), ptx=seed), seed_)
    seed_com = com1 + com2
    return seed_com


class PRG:
    def __init__(self, params):
        self._params = params

    @property
    def params(self):
        return self._params
    
    def __call__(self, salt, e, seed, n_bytes):
        par = self.params
        from math import ceil
        n_blocks = ceil(n_bytes / par.lda)
        stream = b''
        seed_ = lin_ortho(seed)
        for i in range(n_blocks):
            tweaked_salt = tweak_salt(self.params, salt, 3, e, i)
            stream += xor(par.enc(key=tweaked_salt, ptx=seed), seed_)
        return stream[:n_bytes]
