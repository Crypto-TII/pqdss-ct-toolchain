from .parsing import serialize, ByteStrFrmt, VectorFrmt, MatrixFrmt, ArrayFrmt
from .utils import Array, Arrays
from .bits import map_to_bits, truncate_bits_and_pad, bytestring_to_bitstring, bitstring_to_integer
from math import ceil
from numpy import matmul

class MQOM2:
    def __init__(self, params, random_bytes):
        self.params = params
        self.random_bytes = random_bytes

        par = params

        ### Define all the data format we use in the scheme
        # Format of the unitary data
        mq_solution_format = VectorFrmt(par.base_field, par.n) # x
        mq_output_format = VectorFrmt(par.base_field, par.m) # y
        mseed_eq_format = ByteStrFrmt(2*par.lda) # mseed_eq
        digest_format = ByteStrFrmt(2*par.lda)
        salt_format = ByteStrFrmt(par.lda)
        nonce_format = ByteStrFrmt(4)
        
        # Format of the structures (pk, sk, sig, ...)
        self.pk_format = ArrayFrmt(
            mseed_eq_format, # mseed_eq
            mq_output_format, # y
        )
        self.sk_format = ArrayFrmt(
            ByteStrFrmt(self.pk_format.get_bytesize()), # pk
            mq_solution_format, # x
        )
        self.sig_format = ArrayFrmt(
            salt_format, # salt
            digest_format, # com1
            digest_format, # com2
            ArrayFrmt(*[ # alpha1
                VectorFrmt(par.extension_field, par.eta)
                for _ in range(par.tau)
            ]),
            ByteStrFrmt(self.blc.get_opening_bytesize()), # opening
            nonce_format, # nonce
        )
        self.expanded_root_key_format = ArrayFrmt(
            mq_solution_format, # x
            mseed_eq_format, # mseed_eq
        )

    @property
    def blc(self):
        return self.params.blc
    
    @property
    def piop(self):
        return self.params.piop
    
    ########################################
    #####        KEY GENERATION        #####
    ########################################

    def _expand_equations(self, mseed_eq):
        par = self.params
        nc = [(j+1)*par.log2q for j in range(par.n)]
        #nz = [(par.n-(j+1))*par.log2q for j in range(par.n)]
        nb = [ceil(nc[j]/8) for j in range(par.n)]
        nb_eq = nb[par.n-1] + sum(nb)

        seed_eq, A, b = Arrays(3, par.m)
        for i in range(par.m):
            # Expand equation's seed
            seed_eq[i] = par.xof((b'\x01', mseed_eq, map_to_bits(i, 2)), len=par.lda)
            stream = par.prg(b'\x00'*par.lda, 0, seed_eq[i], nb_eq)

            # Parse the pseudorandom bytestring
            k = 0
            matrix_bytes = b''
            for j in range(par.n):
                # Add zero bits to complete each row
                partial_row_bytes = stream[k:k+nb[j]]
                row_bytes = truncate_bits_and_pad(partial_row_bytes, nc[j], par.n*par.log2q)
                matrix_bytes += row_bytes
                k += nb[j]
            A[i] = MatrixFrmt(par.base_field, par.n, par.n).parse(matrix_bytes)
            b[i] = VectorFrmt(par.base_field, par.n).parse(stream[k:])

        return (A, b)

    def generate_keys(self, seed_key=None):
        """ MQOM2 -- Key Generation """
        par = self.params
        seed_key = seed_key or self.random_bytes(2*par.lda)

        # Expand the MQ solution
        expanded_bytesize = self.expanded_root_key_format.get_bytesize()
        x, mseed_eq = self.expanded_root_key_format.parse(
            par.xof(b'\x00', seed_key, len=expanded_bytesize)
        )

        # Expand the MQ instance
        (A, b) = self._expand_equations(mseed_eq)
        y = Array(par.m)
        for i in range(par.m):
            y[i] = matmul(x, matmul(A[i], x)) + matmul(b[i], x)

        # Serialize and define keys
        pk = serialize(mseed_eq, y)
        sk = serialize(pk, x)
        return (pk, sk)
    
    def get_public_key_bytesize(self):
        return self.pk_format.get_bytesize()
    
    def get_secret_key_bytesize(self):
        return self.sk_format.get_bytesize()
    
    ########################################
    #####             SIGN             #####
    ########################################

    def _sample_challenge_with_nonce(self, digest, nonce_bytes):
        par = self.params
        #expanded_bits = bytestring_to_bitstring(par.xof(
        #    (digest, nonce_bytes),
        #    len=ceil((par.tau*par.log2N + par.w)/8),
        #))
        expanded_bytes = par.xof(
            (b'\x05', digest, nonce_bytes),
            len=(par.tau*2 + 2),
        )
        i_star = Array(par.tau)
        for e in range(par.tau):
            i_star[e] = (expanded_bytes[2*e] + 256*expanded_bytes[2*e+1]) % par.N
        val = (expanded_bytes[2*par.tau] + 256*expanded_bytes[2*par.tau+1]) % (2**par.w)
        #k = 0
        #for e in range(par.tau):
        #    i_star[e] = bitstring_to_integer(expanded_bits[k:k+par.log2N])
        #    k += par.log2N
        #val = bitstring_to_integer(expanded_bits[k:k+par.w])
        return (i_star, val)

    def _sample_challenge(self, pk, com1, com2, msg_hash):
        par = self.params
        digest = par.xof((b'\x04', pk, com1, com2, msg_hash), len=2*par.lda)
        nonce = 0
        while True:
            (i_star, val) = self._sample_challenge_with_nonce(digest, map_to_bits(nonce, 4))
            if val == 0:
                return (i_star, map_to_bits(nonce, 4))
            nonce += 1

    def sign(self, sk, msg, mseed=None, salt=None):
        """ MQOM2 -- Signing Algorithm """
        par = self.params

        # Key Parsing & Expansion
        pk, x = self.sk_format.parse(sk)
        mseed_eq, y = self.pk_format.parse(pk)
        (A, b) = self._expand_equations(mseed_eq)

        # Initialization
        mseed = mseed or self.random_bytes(par.lda)
        salt = salt or self.random_bytes(par.lda)
        msg_hash = par.xof(b'\x02', msg, len=2*par.lda)

        # Line/Polynomial Commitment
        (com1, key, x0, u0, u1) = self.blc.commit(mseed, salt, x)

        # PIOP Protocol: Compute Alpha Line
        (alpha0, alpha1) = self.piop.compute_alpha_lines(com1, x, x0, u0, u1, A, b)
        
        # PIOP Queries & Opening
        com2 = par.xof(b'\x03', serialize(alpha0, alpha1), len=2*par.lda)
        (i_star, nonce_bytes) = self._sample_challenge(pk, com1, com2, msg_hash)
        opening = self.blc.open(key, i_star)

        # Serialization
        sig = serialize(salt, com1, com2, alpha1, opening, nonce_bytes)
        return sig
    
    def get_signature_bytesize(self):
        return self.sig_format.get_bytesize()
    
    ########################################
    #####            VERIFY            #####
    ########################################

    def verify(self, pk, msg, sig):
        """ MQOM2 -- Verification Algorithm """
        par = self.params
        mseed_eq, y = self.pk_format.parse(pk)
        (A, b) = self._expand_equations(mseed_eq)
        (salt, com1, com2, alpha1, opening, nonce_bytes) = self.sig_format.parse(sig)
        msg_hash = par.xof(b'\x02', msg, len=2*par.lda)

        digest = par.xof((b'\x04', pk, com1, com2, msg_hash), len=2*par.lda)
        (i_star, val) = self._sample_challenge_with_nonce(digest, nonce_bytes)
        if val != 0:
            return False
        
        (ret, x_eval, u_eval) = self.blc.eval(salt, com1, opening, i_star)
        if ret is not True:
            return False
        
        alpha0 = self.piop.recompute_alpha_lines(com1, alpha1, i_star, x_eval, u_eval, A, b, y)
        com2_ = par.xof(b'\x03', serialize(alpha0, alpha1), len=2*par.lda)
        if com2_ != com2:
            return False
        
        return True
