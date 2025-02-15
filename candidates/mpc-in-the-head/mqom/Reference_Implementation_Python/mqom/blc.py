from .parsing import parse, serialize, expand_seed, ByteStrFrmt, VectorFrmt, ArrayFrmt
from .bits import split_in_two, pad_left
from .utils import MultiDimArrays, Arrays
from .seeds import tweak_salt, seed_commit

class BLC:
    def __init__(self, params):
        self._params = params

        par = self.params
        mq_solution_format = VectorFrmt(par.base_field, par.n)
        self._x_format = mq_solution_format
        self._u_format = VectorFrmt(par.extension_field, par.eta)

        self._opening_format = ArrayFrmt( # decom
            ArrayFrmt(*[
                ByteStrFrmt(par.log2N*par.lda) # path
                for _ in range(par.tau)
            ]),
            ArrayFrmt(*[
                ByteStrFrmt(2*par.lda) # out_ls_com
                for _ in range(par.tau)
            ]),
            ArrayFrmt(*[
                ByteStrFrmt(mq_solution_format.get_bytesize()-par.lda) # Delta_x_
                for _ in range(par.tau)
            ]),
        )

    @property
    def params(self):
        return self._params

    @property
    def prg(self):
        return self.params.prg

    @property
    def ggmtree(self):
        return self.params.ggmtree

    @property
    def x_format(self):
        return self._x_format

    @property
    def u_format(self):
        return self._u_format
    
    def get_opening_bytesize(self):
        return self._opening_format.get_bytesize()

    ########################################
    #####         SUB-ROUTINES         #####
    ########################################
    
    def _tweak_salt(self, salt, e):
        return tweak_salt(self.params, salt, 0, e, 0)
    
    def _seed_commit(self, salt, seed):
        return seed_commit(self.params, salt, seed)

    ########################################
    #####            COMMIT            #####
    ########################################

    def commit(self, mseed, salt, x):
        """ Commit two random vector polynomials P_x and P_u
            such that P_x(X) := x*X + x0 and P_u(X) :=
        """

        par = self.params
        delta, x_ = split_in_two(serialize(x), par.lda)

        # Expand the randomness for all the parallel seed trees
        rseed = expand_seed(self.prg, mseed, *[ByteStrFrmt(par.lda)]*par.tau)

        tree, lseed, u0, u1, x0, Delta_x, Delta_x_, hash_ls_com = Arrays(8, par.tau)
        ls_com, exp, bar_x, bar_u = MultiDimArrays(4, (par.tau, par.N))
        for e in range(par.tau):
            # Expand a seed tree such that the XOR of all the leaves is equal to delta
            tree[e], lseed[e] = self.ggmtree.expand(salt, rseed[e], e, delta)

            # Commit all the seeds and expand them
            tweaked_salt = self._tweak_salt(salt, e)
            for i in range(par.N):
                ls_com[e][i] = self._seed_commit(tweaked_salt, lseed[e][i])
                expansion_bytesize = self.x_format.get_bytesize() + self.u_format.get_bytesize() - par.lda
                exp[e][i] = self.prg(salt, e, lseed[e][i], expansion_bytesize)
                bar_x[e][i], bar_u[e][i] = parse(lseed[e][i] + exp[e][i], self.x_format, self.u_format)
            hash_ls_com[e] = par.xof(b'\x06', ls_com[e], len=2*par.lda)

            # Compute P_u
            u0[e] = [
                - sum(par.omega[i]*bar_u[e][i][j] for i in range(par.N))
                for j in range(par.eta)
            ]
            u1[e] = [
                sum(bar_u[e][i][j] for i in range(par.N))
                for j in range(par.eta)
            ]

            # Compute P_x
            x0[e] = [
                - sum(par.omega[i]*bar_x[e][i][j] for i in range(par.N))
                for j in range(par.n)
            ]
            Delta_x[e] = [
                x[j] - sum(bar_x[e][i][j] for i in range(par.N))
                for j in range(par.n)
            ]
            zero, Delta_x_[e] = split_in_two(serialize(Delta_x[e]), par.lda)
            assert zero == b'\x00'*len(zero)

        com = par.xof((b'\x07', hash_ls_com, Delta_x_), len=2*par.lda)
        key = (tree, ls_com, Delta_x_)
        return (com, key, x0, u0, u1)
    
    ########################################
    #####             OPEN             #####
    ########################################

    def open(self, key, i_star):
        """ Open evaluation of index i_star[e] for the e-th parallel commitment """
        (tree, ls_com, Delta_x_) = key
        par = self.params

        path, out_ls_com = Arrays(2, par.tau)
        for e in range(par.tau):
            path[e] = self.ggmtree.open(tree[e], i_star[e])
            out_ls_com[e] = ls_com[e][i_star[e]]
        
        opening = serialize(path, out_ls_com, Delta_x_)
        return opening
    
    ########################################
    #####             OPEN             #####
    ########################################

    def eval(self, salt, com, opening, i_star):
        """ Get the opened evaluations """
        (path, out_ls_com, Delta_x_) = self._opening_format.parse(opening)
        par = self.params

        lseed, Delta_x, x_eval, u_eval, hash_ls_com = Arrays(5, par.tau)
        ls_com, exp, bar_x, bar_u = MultiDimArrays(4, (par.tau, par.N))
        for e in range(par.tau):
            lseed[e] = self.ggmtree.partially_expand(salt, path[e], e, i_star[e])

            tweaked_salt = self._tweak_salt(salt, e)
            for i in range(par.N):
                if i != i_star[e]:
                    ls_com[e][i] = self._seed_commit(tweaked_salt, lseed[e][i])
                    expansion_bytesize = self.x_format.get_bytesize() + self.u_format.get_bytesize() - par.lda
                    exp[e][i] = self.prg(salt, e, lseed[e][i], expansion_bytesize)
                    bar_x[e][i], bar_u[e][i] = parse(lseed[e][i] + exp[e][i], self.x_format, self.u_format)
            ls_com[e][i_star[e]] = out_ls_com[e]
            hash_ls_com[e] = par.xof(b'\x06', ls_com[e], len=2*par.lda)

            r = par.omega[i_star[e]]
            Delta_x[e] = self.x_format.parse(pad_left(Delta_x_[e], par.lda))
            x_eval[e] = [
                Delta_x[e][j]*r + sum(bar_x[e][i][j]*(r-par.omega[i]) for i in range(par.N) if i != i_star[e])
                for j in range(par.n)
            ]
            u_eval[e] = [
                sum(bar_u[e][i][j]*(r-par.omega[i]) for i in range(par.N) if i != i_star[e])
                for j in range(par.eta)
            ]

        com_ = par.xof((b'\x07', hash_ls_com, Delta_x_), len=2*par.lda)
        if com != com_:
            return (False, None, None)
        
        return (True, x_eval, u_eval)
