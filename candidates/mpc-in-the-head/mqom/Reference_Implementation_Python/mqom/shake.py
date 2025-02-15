def SHAKE128(*args, len=None):
    assert len is not None, 'SHAKE128 requires a output bytesize as input'
    import hashlib
    m = hashlib.shake_128()
    def rec(*args):
        for arg in args:
            if type(arg) not in [list, tuple]:
                m.update(arg)
            else:
                rec(*arg)
    rec(*args)
    return m.digest(len)

def SHAKE256(*args, len=None):
    assert len is not None, 'SHAKE256 requires a output bytesize as input'
    import hashlib
    m = hashlib.shake_256()
    def rec(*args):
        for arg in args:
            if type(arg) not in [list, tuple]:
                m.update(arg)
            else:
                rec(*arg)
    rec(*args)
    return m.digest(len)
