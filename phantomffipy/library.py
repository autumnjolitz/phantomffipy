'''Let's import this!'''

import os.path
from cffi import FFI


def read_headers():
    '''open up the header of the library,
    strip out the extern "C" {..} that encloses
    the good stuff'''
    with open(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            'phantompy.hpp'), 'r') as fh:
        c_headers = None
        for line in fh:
            if 'extern "C" {' in line:
                c_headers = ''
                continue
            if '}' in line:
                break
            if c_headers is not None:
                c_headers += line
    return c_headers


def acquire_library():
    '''
    >>> ffi, lib = acquire_library()
    >>> ffi is not None
    True
    >>> lib is not None
    True
    '''
    ffi = FFI()
    ffi.cdef(read_headers())
    return ffi, ffi.dlopen(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)), 'libphantompy'))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
