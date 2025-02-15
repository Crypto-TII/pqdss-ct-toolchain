from .parsing import MatrixFrmt
from .utils import Array, Arrays
from .params import Variant
from numpy import matmul, array

class PIOP:
    def __init__(self, params):
        self._params = params
        self._Gamma_format = MatrixFrmt(params.extension_field, params.eta, params.m//params.mu)

    @property
    def params(self):
        return self._params
            
    def _Phi(self, vec):
        par = self.params
        assert len(vec) % par.mu == 0
        return [
            sum(
                par.phi_base[j]*vec[i*par.mu+j]
                for j in range(par.mu)
            ) for i in range(len(vec) // par.mu)
        ]
    
    def _identity_matrix(self, size):
        par = self.params
        return [
            [
                par.extension_field(int(i == j))
                for j in range(size)
            ] for i in range(size)
        ]

    ########################################
    #####      COMPUTE ALPHA LINES     #####
    ########################################

    def _compute_pz(self, x0_e, x, A, b):
        par = self.params

        z0, z1 = Arrays(2, par.m)
        for i in range(par.m):
            # Compute P_t(X) = t0 + t1·X = A_i·P_x(X) + b_i·X
            t0 = matmul(A[i], x0_e)
            t1 = matmul(A[i], x) + b[i]
            # Compute P_z(X) = z0 + z1·X = P_t(X)^T P_x(X) - y_i·X^2
            z0[i] = matmul(t0, x0_e)
            z1[i] = matmul(t0, x) + matmul(t1, x0_e)

        return (z0, z1)

    def compute_alpha_lines(self, com, x, x0, u0, u1, A, b):
        par = self.params

        # Get the Gamma (batching) matrix
        if par.variant == Variant.R5:
            Gamma_bytestring = par.xof(b'\x08', com, len=self._Gamma_format.get_bytesize())
            Gamma = self._Gamma_format.parse(Gamma_bytestring)
        elif par.variant == Variant.R3:
            assert par.m//par.mu == par.eta
            Gamma = self._identity_matrix(par.eta)

        # Compute the line alpha
        alpha0, alpha1 = Arrays(2, par.tau)
        for e in range(par.tau):
            z0, z1 = self._compute_pz(x0[e], x, A, b)
            alpha0[e] = list(u0[e] + matmul(Gamma, self._Phi(z0)))
            alpha1[e] = list(u1[e] + matmul(Gamma, self._Phi(z1)))

        return (alpha0, alpha1)
            
    ########################################
    #####     RECOMPUTE ALPHA LINES    #####
    ########################################

    def _compute_pz_eval(self, r, v_x, A, b, y):
        par = self.params

        v_z = Array(par.m)
        for i in range(par.m):
            # v_t = P_t(r) = A_i·P_x(r) + b_i·r
            v_t = matmul(A[i], v_x) + array(b[i])*r
            # v_z = P_z(r) = v_t^T P_x(r) - y_i·r^2
            v_z[i] = matmul(v_t, v_x) - y[i]*r**2
        
        return v_z

    def recompute_alpha_lines(self, com, alpha1, i_star, x_eval, u_eval, A, b, y):
        par = self.params

        # Get the Gamma (batching) matrix
        if par.variant == Variant.R5:
            Gamma_bytestring = par.xof(b'\x08', com, len=self._Gamma_format.get_bytesize())
            Gamma = self._Gamma_format.parse(Gamma_bytestring)
        elif par.variant == Variant.R3:
            assert par.m//par.mu == par.eta
            Gamma = self._identity_matrix(par.eta)

        # Compute evaluation of the line alpha
        alpha0 = Array(par.tau)
        for e in range(par.tau):
            r = par.omega[i_star[e]] # evaluation point
            v_z = self._compute_pz_eval(r, x_eval[e], A, b, y)
            v_alpha = u_eval[e] + matmul(Gamma, self._Phi(v_z))
            alpha0[e] = list(v_alpha - array(alpha1[e])*r)
        
        return alpha0
