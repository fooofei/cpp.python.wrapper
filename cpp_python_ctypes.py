# coding=utf-8
'''

 compatible with python 2,3

'''

import ctypes
import os
import sys
from io_in_out import io_in_arg
from io_in_out import io_bytes_arg
from io_in_out import io_out_code
from io_in_out import io_out_arg
from io_in_out import io_print
from io_in_out import pyver
from io_in_out import io_stderr_print

from ctypes import c_uint
from ctypes import c_int
from ctypes import memset
from ctypes import addressof
from ctypes import create_string_buffer
from ctypes import c_char_p
from ctypes import c_void_p
from ctypes import POINTER
from ctypes import pointer
from ctypes import c_wchar_p
from ctypes import sizeof

curpath = os.path.dirname(os.path.realpath(__file__))
curpath = io_in_arg(curpath)

if os.name == 'nt':
    from ctypes import WINFUNCTYPE as ExportFuncType
    from ctypes import windll as library_loader
else:
    from ctypes import CFUNCTYPE as ExportFuncType
    from ctypes import cdll as library_loader


def ctypes_cast_c_void_p(v):
    return ctypes.cast(v, ctypes.c_void_p)


# cast 为 ctypes.c_char_p 无法打印整型的地址，会把字符串输出
def bytes_string_address(v): return ctypes_cast_c_void_p(v)


def bytes_string_address2(v):
    return ctypes.cast(
        ctypes.cast(v, ctypes.c_char_p)
        , ctypes.c_void_p)


def bytes_string_2_ctypes_c_char_p(v):
    # 我怕直接 ctypes.cast(v,ctypes.c_char_p) 会有内存申请
    return ctypes.cast(
        bytes_string_address(v)
        , ctypes.c_char_p
    )


# 知道上面两个等价后 下面这个我们就放心使用了
def text_string_address(v):
    return ctypes.cast(ctypes.cast(v, ctypes.c_wchar_p), ctypes.c_void_p)


def ctypes_memory_view(addr, addr_size):
    ''' Read addr memory, not copy.
    addr: int
    addr_size: int, not ctypes.c_uint
    '''
    return (ctypes.c_ubyte * addr_size).from_address(addr)


class CppExportStructure(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('cb', c_uint),
        ('pfn_func_empty', ExportFuncType(c_int)),
        ('pfn_func_change_value_int', ExportFuncType(c_int, POINTER(c_uint))),
        ('pfn_func_in_memory', ExportFuncType(c_int, c_char_p, c_uint)),
        ('pfn_func_in_memoryw', ExportFuncType(c_int, c_wchar_p, c_uint)),
        ('pfn_func_out_memory_noalloc', ExportFuncType(c_int, POINTER(c_void_p), POINTER(c_uint))),
        ('pfn_func_out_memory_alloc', ExportFuncType(c_uint, c_void_p, POINTER(c_uint))),
    ]

    def __init__(self):
        self.reset()

    def loadlib(self, fullpath_dll):
        p = io_out_arg(fullpath_dll, pfn_check=os.path.exists)
        lib = library_loader.LoadLibrary(p)
        if not lib:
            raise ValueError('fail load')

        hr = lib.InitExportFunctions(pointer(self))

        assert hr == 0
        return (hr, 0)

    def reset(self):
        memset(addressof(self), 0, sizeof(CppExportStructure))
        self.cb = sizeof(CppExportStructure)

    def empty(self):
        hr = self.pfn_func_empty()
        assert (hr == 0)
        return (hr, 0)

    def change_value_int(self, value):
        ''' A value in python , pass to cpp, change it in cpp, and see the change in python '''
        v = c_uint(value)
        # POINTER() 比 pointer() 速度快，但功能少, POINTER() 适合不修改传入参数时使用
        hr = self.pfn_func_change_value_int(pointer(v))
        assert (hr == 0)
        return (hr, v.value)

    def pass_python_bytes_string(self, bytes_string):
        '''A memory(void * or char * or byte *) in python, pass it to cpp only for read

           Also we can use
           addr = c_char_p(bytes_string)
           but it will do copy, alloc memory.
        '''
        addr = bytes_string_2_ctypes_c_char_p(bytes_string)
        # 非必须
        # addr_size=ctypes.c_uint(len(bytes_string))
        hr = self.pfn_func_in_memory(addr, len(bytes_string))
        assert (hr == 0)
        return (hr,)

    def pass_python_unicode_string(self, unicode_string):
        ''' A wchar_t string value in python, pass it to cpp only for read
        '''

        # Can not use pystring_as_string_size
        addr_buffer = ctypes.create_unicode_buffer(unicode_string)
        # addr_buffer = ctypes.c_wchar_p(unicode_string)
        # In Visual Studio, debug it, see the unicode is utf16(2 bytes)
        hr = self.pfn_func_in_memoryw(addr_buffer, len(unicode_string))
        assert (hr == 0)
        return (hr,)

    def out_memory_python_noalloc(self):
        '''return a memory address and size from cpp, only read in python'''

        addr = ctypes.c_void_p(0)
        addr_size = ctypes.c_uint(0)
        pfn = self.pfn_func_out_memory_noalloc
        hr = pfn(ctypes.pointer(addr), ctypes.pointer(addr_size))
        assert (hr == 0 and addr_size.value > 0)
        io_print(u'python_print->ctypes 从 cpp 返回的字符串内存地址 {}'.format(
            hex(addr.value)
        ))
        vm = ctypes_memory_view(addr.value, addr_size.value)
        # Cast const void * -> const char *
        v = ctypes.cast(vm, ctypes.c_char_p)
        return (hr, v.value)

    def out_memory_python_alloc(self):
        ''' Alloc memory in python, pass it to cpp modify it. '''

        addr_size = ctypes.c_uint(0)
        pfn = self.pfn_func_out_memory_alloc
        hr = pfn(ctypes.c_void_p(0), pointer(addr_size))
        assert (hr == 0 and addr_size.value > 0)
        addr = ctypes.create_string_buffer(addr_size.value)
        io_print(u'python_print->ctypes 提供申请的字符串内存地址 {}'.format(
            hex(ctypes.addressof(addr))
        ))
        hr = pfn(addr, pointer(addr_size))
        assert (hr == 0)
        return (hr, addr.value)
