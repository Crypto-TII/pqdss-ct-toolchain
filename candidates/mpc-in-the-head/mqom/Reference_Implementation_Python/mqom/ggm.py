from .bits import xor, split_in_two
from .seeds import tweak_salt, seed_derive

class GGMTree:
    def __init__(self, params):
        self._params = params

    @property
    def params(self):
        return self._params

    ########################################
    #####         SUB-ROUTINES         #####
    ########################################

    def _tweak_salt(self, salt, e, j):
        return tweak_salt(self.params, salt, 2, e, j-1)
    
    def _seed_derive(self, salt, seed):
        return seed_derive(self.params, salt, seed)

    ########################################
    #####            EXPAND            #####
    ########################################

    def expand(self, salt, root_seed, idx_rep, delta):
        par = self.params
        # Expand the GGM tree
        tree = [None]*(2*par.N)
        tree[2] = root_seed
        tree[3] = xor(root_seed, delta)
        for j in range(1, par.log2N):
            twk_salt = self._tweak_salt(salt, idx_rep, j)
            for k in range(2**j, 2**(j+1)):
                tree[2*k] = self._seed_derive(twk_salt, tree[k])
                tree[2*k+1] = xor(tree[2*k], tree[k])
        lseeds = tree[par.N:]
        return (tree, lseeds)
    
    ########################################
    #####             OPEN             #####
    ########################################

    def open(self, tree, hidden_idx):
        par = self.params
        path = b''
        hidden_node = par.N + hidden_idx
        for _ in range(par.log2N):
            path += tree[hidden_node ^ 0x01]
            hidden_node >>= 1
        return path

    ########################################
    #####       PARTIALLY EXPAND       #####
    ########################################
        
    def partially_expand(self, salt, path, idx_rep, hidden_idx):
        par = self.params
        # Expand the GGM tree
        tree = [None]*(2*par.N)
        hidden_node = par.N + hidden_idx
        for _ in range(par.log2N):
            tree[hidden_node ^ 0x01], path = split_in_two(path, par.lda)
            hidden_node >>= 1
        for j in range(1, par.log2N):
            twk_salt = self._tweak_salt(salt, idx_rep, j)
            for k in range(2**j, 2**(j+1)):
                if tree[k] != None:
                    tree[2*k] = self._seed_derive(twk_salt, tree[k])
                    tree[2*k+1] = xor(tree[2*k], tree[k])
        lseeds = tree[par.N:]
        return lseeds
