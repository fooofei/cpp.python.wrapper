#coding=utf-8
'''

 compatible with python 2,3

'''

from __future__ import unicode_literals

import ctypes
import os
import sys

from io_in_out import *


curpath = os.path.dirname(os.path.realpath(__file__))

def io_ctypes_c_char_p(arg):
    global pyver
    if pyver >= 3:
        return c_char_p(io_bytes_arg(io_in_arg(arg)))
    else:
        return c_char_p(io_bytes_arg(arg))


curpath = io_in_arg(curpath)


from ctypes import c_uint, c_int, c_void_p, POINTER, \
    c_char_p, sizeof, memset, addressof, \
    pointer, create_string_buffer, byref, \
    c_char, c_wchar_p, c_ubyte, c_double

if os.name == 'nt':
    from ctypes import WINFUNCTYPE as ExportFuncType
    from ctypes import windll as library_loader
else:
    from ctypes import CFUNCTYPE as ExportFuncType
    from ctypes import cdll as library_loader

if '__pypy__' in sys.builtin_module_names:
    class PyDLL(ctypes.CDLL):
        _func_flags_ = ctypes._FUNCFLAG_CDECL | ctypes._FUNCFLAG_PYTHONAPI


    if os.name in ("nt", "ce"):
        pythonapi = PyDLL("libpypy-c.dll")
    else:
        pythonapi = PyDLL('libpypy-c.so')
    PyString_AsStringAndSize = pythonapi.PyPyString_AsStringAndSize

else:
    pythonapi = ctypes.pythonapi
    if pyver >= 3:
        func = pythonapi.PyBytes_AsStringAndSize
    elif pyver == 2:
        func = pythonapi.PyString_AsStringAndSize
    else:
        func = pythonapi.PyString_AsStringAndSize

    PyString_AsStringAndSize = func

if hasattr(pythonapi, 'Py_InitModule4'):
    Py_ssize_t = ctypes.c_int
elif hasattr(pythonapi, 'Py_InitModule4_64'):
    Py_ssize_t = ctypes.c_int64
else:
    Py_ssize_t = ctypes.c_int
    # raise TypeError("Cannot determine type of Py_ssize_t")

# pypy 里的 py_object 不能传递 str ，死路了

PyString_AsStringAndSize.restype = ctypes.c_int
PyString_AsStringAndSize.argtypes = [ctypes.py_object,
                                     ctypes.POINTER(
                                         ctypes.POINTER(ctypes.c_char)),
                                     ctypes.POINTER(Py_ssize_t)]


def pystring_as_string_size(pystring):
    if not isinstance(pystring, io_out_code):
        raise ValueError('arg must be {0}'.format(io_out_code))
    addr = POINTER(c_char)()
    size = Py_ssize_t(0)

    hr = PyString_AsStringAndSize(pystring, pointer(addr), pointer(size))
    return (hr, addr, c_uint(size.value))


class CppExportStructure(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('cb',c_uint),
        ('pfn_func_empty',ExportFuncType(c_int)),
        ('pfn_func_change_value_int',ExportFuncType(c_int,POINTER(c_uint))),
        ('pfn_func_in_memory',ExportFuncType(c_int,c_char_p,c_uint)),
        ('pfn_func_in_memoryw',ExportFuncType(c_int,c_wchar_p,c_uint)),
        ('pfn_func_out_memory_noalloc',ExportFuncType(c_int,POINTER(c_void_p),POINTER(c_uint))),
        ('pfn_func_out_memory_alloc',ExportFuncType(c_uint,c_void_p,POINTER(c_uint))),
    ]

    def __init__(self):
        self.reset()


    def load(self):
        a = {'nt':'debug\\cpp_python.dll'}
        p = os.path.join(curpath,a.get(os.name,'libcpp_python.so'))
        p = io_out_arg(p, pfn_check=os.path.exists)
        lib = library_loader.LoadLibrary(p)
        if not lib :
            raise ValueError('fail load')
        hr = lib.InitExportFunctions(pointer(self))
        assert hr == 0

    def reset(self):
        memset(addressof(self),0,sizeof(CppExportStructure))
        self.cb = sizeof(CppExportStructure)

    def test_func_empty(self):
        hr = self.pfn_func_empty()
        assert hr == 0
        io_print('')


    def test_func_change_value_int(self):
        ''' a value in python , pass to cpp, change it in cpp, and see the change in python '''
        v = c_uint(0)
        # POINTER() 比 pointer() 速度快，但功能少, POINTER() 适合不修改传入参数时使用
        hr = self.pfn_func_change_value_int(pointer(v))
        assert hr ==0
        io_print('test_func_change_value_int: 0->{0}'.format(v.value))

    def test_func_in_memory(self):
        '''a memory(void * or char * or byte *) in python, pass it to cpp only for read'''
        value = 'this is string in python test_func_in_memory'
        hr , addr, size = pystring_as_string_size(io_bytes_arg(value))
        assert hr == 0

        # also can use
        # addr, size = c_char_p(io_bytes_arg(value)), c_uint(len(value))
        # The use of pystring_as_string_size() can save a lot of memory

        hr = self.pfn_func_in_memory(addr,size)
        assert hr == 0
        io_print('')

    def test_func_in_memoryw(self):
        ''' a wchar_t type value in python, pass it to cpp only for read'''
        value = 'this is string in python test_func_in_memoryw'

        # can not use pystring_as_string_size
        addr,size = c_wchar_p(value), c_uint(len(value))
        hr = self.pfn_func_in_memoryw(addr,size)
        assert hr ==0
        io_print('')

    def test_func_out_memory_noalloc(self):
        '''return a memory address and size from cpp, only read in python'''
        ptr = c_void_p(0)
        ptr_size = c_uint(0)
        hr = self.pfn_func_out_memory_noalloc(pointer(ptr),pointer(ptr_size))
        assert  hr ==0 and ptr.value and ptr_size.value

        memory_for_read = (ctypes.c_ubyte * ptr_size.value).from_address(ptr.value)
        # cast const void * to const char *
        v = ctypes.cast(memory_for_read,ctypes.c_char_p)
        io_print(v.value)

    def test_func_out_memory_alloc(self):
        ''''''
        ptr_size = c_uint(0)
        # first call get size
        hr = self.pfn_func_out_memory_alloc(c_void_p(0),pointer(ptr_size))
        assert  hr ==0 and ptr_size.value
        ptr = create_string_buffer(ptr_size.value)
        # second get memory address
        hr = self.pfn_func_out_memory_alloc(ptr,pointer(ptr_size))
        assert hr==0 and ptr_size.value
        io_print(ptr.value)


def entry():
    a = CppExportStructure()
    a.load()
    a.test_func_empty()
    a.test_func_change_value_int()
    a.test_func_in_memory()
    a.test_func_in_memoryw()
    a.test_func_out_memory_noalloc()
    a.test_func_out_memory_alloc()

if __name__ == '__main__':
    entry()