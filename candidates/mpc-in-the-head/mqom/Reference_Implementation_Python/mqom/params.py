from enum import Enum

class Category(Enum):
    I   = 'CAT-I'
    III = 'CAT-III'
    V   = 'CAT-V'

class Variant(Enum):
    R3 = '5r'
    R5 = '3r'

class TradeOff(Enum):
    SHORT = 'short'
    FAST = 'fast'

class MQOM2Parameters:
    def __init__(self, lda, base_field, n, tau, N, extension_field, eta, w, variant, phi_base):
        assert lda in [16, 24, 32]
        self._lda = lda
        self._base_field = base_field
        self._n = n
        self._tau = tau
        self._N = N
        self._extension_field = extension_field
        self._eta = eta
        self._variant = variant
        self._w = w
        self._phi_base = phi_base

        from .field import BinaryField
        assert issubclass(base_field, BinaryField)
        assert issubclass(extension_field, BinaryField)
        assert extension_field.bitsize % base_field.bitsize == 0

        from math import log2
        q = base_field.order()
        log2q = base_field.bitsize
        mu = extension_field.bitsize // base_field.bitsize
        self._q = q
        self._log2q = log2q
        self._mu = mu
        assert n % mu == 0, 'n should be a multiple mu'
        assert len(phi_base) == mu
        if variant == Variant.R3:
            assert n//mu == eta

        from math import log2
        self._log2N = round(log2(N))
        assert N == 2**self._log2N

        from .ggm import GGMTree
        from .seeds import PRG
        from .blc import BLC
        from .piop import PIOP
        from .rijndael import AES128, Rijndael256_256_Trun192, Rijndael256_256
        from .shake import SHAKE128, SHAKE256
        self._enc = {
            16: AES128,
            24: Rijndael256_256_Trun192,
            32: Rijndael256_256,
        }[lda]
        self._ggmtree = GGMTree(params=self)
        self._prg = PRG(params=self)
        self._xof = {
            16: SHAKE128,
            24: SHAKE256,
            32: SHAKE256,
        }[lda]
        self._blc = BLC(params=self)
        self._piop = PIOP(params=self)

        if self.extension_field is not None:
            self._omega = []
            for i in range(N):
                self._omega.append(extension_field(i))
            assert len(self.omega) == N
        else:
            self._omega = None

    @property
    def lda(self):
        return self._lda
     
    @property
    def base_field(self):
        return self._base_field
     
    @property
    def n(self):
        return self._n
     
    @property
    def m(self):
        # The number of MQ equations is the same than the number of MQ unknowns
        return self._n
     
    @property
    def tau(self):
        return self._tau
    
    @property
    def N(self):
        return self._N

    @property
    def extension_field(self):
        return self._extension_field
    
    @property
    def eta(self):
        return self._eta
    
    @property
    def w(self):
        return self._w
    
    @property
    def phi_base(self):
        return self._phi_base
    
    @property
    def variant(self):
        return self._variant
    
    @property
    def q(self):
        return self._q
    
    @property
    def log2q(self):
        return self._log2q
    
    @property
    def mu(self):
        return self._mu
    
    @property
    def log2N(self):
        return self._log2N
    
    @property
    def enc(self):
        return self._enc
    
    @property
    def ggmtree(self):
        return self._ggmtree

    @property
    def prg(self):
        return self._prg
    
    @property
    def xof(self):
        return self._xof
    
    @property
    def blc(self):
        return self._blc
    
    @property
    def piop(self):
        return self._piop
    
    @property
    def omega(self):
        return self._omega

    @classmethod
    def get(cls, cat, field_size, tradeoff, variant):
        from .field import F2, F2to8, F2to16

        lda = {
            Category.I: 16,
            Category.III: 24,
            Category.V: 32,
        }[cat]

        # Base Field
        if field_size == 2:
            F = F2
            n = {
                Category.I:   160,
                Category.III: 240,
                Category.V:   320,
            }[cat]
        elif field_size == 256:
            F = F2to8
            n = {
                Category.I:   48,
                Category.III: 72,
                Category.V:   96,
            }[cat]
        else:
            raise ValueError(f'No instance with |F|={field_size}')

        # Trade-off
        if tradeoff == TradeOff.SHORT:
            N = 2048
            tau = {
                Category.I:   12,
                Category.III: 18,
                Category.V:   25,
            }[cat]
            K = F2to16
            if variant == Variant.R5:
                eta = {
                    Category.I:    8,
                    Category.III: 12,
                    Category.V:   16,
                }[cat]
            elif variant == Variant.R3:
                if field_size == 2:
                    eta = n // 16
                elif field_size == 256:
                    eta = n // 2
            w = {
                Category.I:    8,
                Category.III: 12,
                Category.V:    6,
            }[cat]
            if field_size == 2:
                phi_base = [
                    K(256**i + 2**j)
                    for i in range(2)
                    for j in range(8)
                ]
            elif field_size == 256:
                phi_base = [
                    K(256**i)
                    for i in range(2)
                ]
        elif tradeoff == TradeOff.FAST:
            N = 256
            tau = {
                Category.I:   17,
                Category.III: 27,
                Category.V:   36,
            }[cat]
            K = F2to8
            if variant == Variant.R5:
                eta = {
                    Category.I:   16,
                    Category.III: 24,
                    Category.V:   32,
                }[cat]
            elif variant == Variant.R3:
                if field_size == 2:
                    eta = n // 8
                elif field_size == 256:
                    eta = n
            w = {
                Category.I:   9,
                Category.III: 3,
                Category.V:   4,
            }[cat]
            if field_size == 2:
                phi_base = [
                    K(2**j)
                    for j in range(8)
                ]
            elif field_size == 256:
                phi_base = [K(1)]

        return cls(
            lda=lda, base_field=F, n=n, tau=tau, N=N,
            extension_field=K, eta=eta, w=w, variant=variant,
            phi_base = phi_base,
        )
