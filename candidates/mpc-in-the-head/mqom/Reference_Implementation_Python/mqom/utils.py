def MultiDimArray(dims, init=None):
    if len(dims) == 1:
        return [init]*dims[0]
    return [MultiDimArray(dims[1:], init) for _ in range(dims[0])]

def MultiDimArrays(nb, dims, init=None):
    return tuple(MultiDimArray([nb]+list(dims), init=init))

def Array(size, init=None):
    return MultiDimArray((size,), init=init)

def Arrays(nb, size, init=None):
    return tuple(MultiDimArray((nb, size), init=init))
