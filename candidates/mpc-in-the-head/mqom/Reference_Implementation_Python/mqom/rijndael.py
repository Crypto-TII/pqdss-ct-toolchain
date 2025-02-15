#!/usr/bin/env python3

import numpy as np
import functools

class Rijndael:
    NB_ROUNDS_PER_SIZE = {
        4: {4: 10, 6: 12, 8: 14},
        6: {4: 12, 6: 12, 8: 14},
        8: {4: 14, 6: 14, 8: 14},
    }

    S_BOX = (
        0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
        0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
        0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
        0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
        0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
        0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
        0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
        0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
        0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
        0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
        0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
        0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
        0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
        0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
        0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
        0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
    )

    R_CON = (
        0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
        0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A,
        0x2F, 0x5E, 0xBC, 0x63, 0xC6, 0x97, 0x35, 0x6A,
        0xD4, 0xB3, 0x7D, 0xFA, 0xEF, 0xC5, 0x91, 0x39,
    )

    def __init__(self, n_k, n_b):
        """
        n_k: byte size of the key
        n_b: byte size of the block
        """
        assert n_k in self.NB_ROUNDS_PER_SIZE
        assert n_b in self.NB_ROUNDS_PER_SIZE[n_k]
        self.n_k = n_k
        self.n_b = n_b
        self.n_r = self.NB_ROUNDS_PER_SIZE[n_k][n_b]

    ### Round Transformation
    @classmethod
    def _sub_bytes(cls, s):
        #s[0,:] = [cls.S_BOX[x]for x in s[0,:]]
        #s[1,:] = [cls.S_BOX[x]for x in s[1,:]]
        #s[2,:] = [cls.S_BOX[x]for x in s[2,:]]
        #s[3,:] = [cls.S_BOX[x]for x in s[3,:]]
        s[:,:] = np.vectorize(lambda x: cls.S_BOX[x])(s)

    @staticmethod
    def _shift_rows(s):
        _, Nb = s.shape
        if Nb < 8:
            s[1,:] = np.concatenate((s[1,1:], s[1,:1]))
            s[2,:] = np.concatenate((s[2,2:], s[2,:2]))
            s[3,:] = np.concatenate((s[3,3:], s[3,:3]))
        else:
            s[1,:] = np.concatenate((s[1,1:], s[1,:1]))
            s[2,:] = np.concatenate((s[2,3:], s[2,:3]))
            s[3,:] = np.concatenate((s[3,4:], s[3,:4]))

    @staticmethod
    def _add_round_key(s, k):
        s[:,:] = s[:,:] ^ k[:,:]

    # learned from https://web.archive.org/web/20100626212235/http://cs.ucsb.edu/~koc/cs178/projects/JT/aes.c
    @staticmethod
    def _xtime(a):
        return (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)

    @classmethod
    def _mix_single_column(cls, a):
        # see Sec 4.1.2 in The Design of Rijndael
        t = a[0] ^ a[1] ^ a[2] ^ a[3]
        u = a[0]
        a[0] ^= t ^ cls._xtime(a[0] ^ a[1])
        a[1] ^= t ^ cls._xtime(a[1] ^ a[2])
        a[2] ^= t ^ cls._xtime(a[2] ^ a[3])
        a[3] ^= t ^ cls._xtime(a[3] ^ u)

    @classmethod
    def _mix_columns(cls, s):
        _, Nb = s.shape
        for i in range(Nb):
            cls._mix_single_column(s[:,i])


    ### Key Schedule
    @functools.lru_cache
    def _expand_key(self, key):
        """ Key Expansion.
        Return the subkeys.
        """
        n_b, n_k, n_r = self.n_b, self.n_k, self.n_r
        words = [None]*(n_b*(n_r+1))

        for i in range(n_k):
            words[i] = [key[4*i+0], key[4*i+1], key[4*i+2], key[4*i+3]]

        for i in range(n_k, n_b*(n_r+1)):
            temp = words[i-1]
            if (i % n_k == 0):
                temp = temp[1:] + temp[:1]
                temp = [self.S_BOX[b] for b in temp]
                temp[0] ^= self.R_CON[i // n_k]
            elif (n_k > 6) and (i % n_k == 4):
                temp = [self.S_BOX[b] for b in temp]
            words[i] = [
                words[i-n_k][j] ^ temp[j]
                for j in range(4)
            ]

        return [
            np.array(words[j:j+n_b]).T
            for j in range(0, n_b*(n_r+1), n_b)
        ]
    
    ### Input-Output Formatting
    @staticmethod
    def _bytes2matrix(text):
        """ Convert a byte string into a matrice with 4 rows. The string contains the matrix coefficient in column-major order.
        """
        return np.array(list(text)).reshape(len(text)//4,4).T

    @staticmethod
    def _matrix2bytes(matrix):
        """ Convert a matrice with 4 rows into a byte string. The string contains the matrix coefficient in column-major order.
        """
        return bytes(matrix.T.flat)

    ### Cipher Encryption
    def __call__(self, key, ptx):
        assert len(key) == self.n_k*4
        assert len(ptx) == self.n_b*4

        key_matrices = self._expand_key(key)
        state = self._bytes2matrix(ptx)

        self._add_round_key(state, key_matrices[0])

        for i in range(1, self.n_r):
            self._sub_bytes(state)
            self._shift_rows(state)
            self._mix_columns(state)
            self._add_round_key(state, key_matrices[i])

        self._sub_bytes(state)
        self._shift_rows(state)
        self._add_round_key(state, key_matrices[-1])

        return self._matrix2bytes(state)


class RijndaelTruncated(Rijndael):
    def __init__(self, n_k, n_b, n_t):
        assert n_t <= n_k
        assert n_t <= n_b
        super().__init__(n_k, n_b)
        self.n_t = n_t

    def __call__(self, key, ptx):
        assert len(key) == self.n_t*4
        assert len(ptx) == self.n_t*4

        padded_key = key + b'\x00'*(self.n_k*4-self.n_t*4)
        padded_ptx = ptx + b'\x00'*(self.n_b*4-self.n_t*4)

        padded_ctx = super().__call__(key=padded_key, ptx=padded_ptx)

        return padded_ctx[:self.n_t*4]


AES128 = Rijndael(4,4)
AES192 = Rijndael(6,4)
AES256 = Rijndael(8,4)
Rijndael256_256 = Rijndael(8,8)
Rijndael256_256_Trun192 = RijndaelTruncated(8,8,6)
