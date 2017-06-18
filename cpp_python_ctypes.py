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


def ctypes_api_bytes_string_addr(v):
    ''' Return int '''
    f = ctypes.pythonapi.PyString_AsString
    f.restype = ctypes.c_void_p
    f.argtypes = [ctypes.py_object]
    return f(v)


def _ctypes_api_unicode_string_address_api():
    '''
    Can be error:
        AttributeError: python: undefined symbol: PyUnicodeUCS2_AsUnicode
    '''
    py_unicode_size = ctypes.sizeof(ctypes.c_wchar)
    if py_unicode_size == 2:
        f = ctypes.pythonapi.PyUnicodeUCS2_AsUnicode
    elif py_unicode_size == 4:
        f = ctypes.pythonapi.PyUnicodeUCS4_AsUnicode
    else:
        raise TypeError("Cannot determine wchar_t size")
    f.restype = ctypes.c_void_p
    f.argtypes = [ctypes.py_object]
    return f


def ctypes_api_unicode_string_addr(v):
    '''
    !!!WARNING not always success

    1 Python redefine api PyUnicode_* as PyUnicodeUCS2_* or PyUnicodeUCS4_*,
     so we see the source code is PyUnicode_* , but through ida the lib binary,
     we only find PyUnicodeUCS2_* or PyUnicodeUCS4_*.

    2 Python says, use PyUnicode_FromWideChar/PyUnicode_AsWideChar to support Platform wchar_t.

    3 PyUnicode_FromWideChar/PyUnicode_AsWideChar will copy buffer, which will use external memory.

    4 If the platform sizeof(wchar_t)==4, it can aslo maybe use PyUnicodeUCS2_* apis, by this, we cannot
       get the internal buffer address.
    '''

    try:
        return _ctypes_api_unicode_string_address_api()(v)
    except (TypeError, AttributeError) as er:
        return 0


def bytes_string_address(v):
    return ctypes_api_bytes_string_addr(v)


def text_string_address(v):
    return ctypes_api_unicode_string_addr(v)


def ctypes_addr_as_array(addr, addr_size, element_type):
    ''' Read addr memory, not copy.
    addr: int
    addr_size: int, not ctypes.c_uint
    element_type: ctypes type
    :return <cpp_python_ctypes.c_ubyte_Array_%d>

     # <return_value> not have <return_value>.value
     # len(<return_value>) == addr_size
     # Can use <return_value>[0], <return_value>[1]...
     # Can use for i in <return_value>:
     # Can (base64.b64encode(<return_value>))

    ref https://docs.python.org/2/library/ctypes.html  # Fundamental data types
    element_type=c_ubyte,
        type(<return_value>)=?,
        type(<return_value>[0])=int
        # ctypes.sizeof(<return_value>[0]) # error
        ctypes.sizeof(<return_value>)= ctypes.sizeof(element_type)*len(<return_value>)

    element_type=c_uint,
        type(<return_value>)=?,
        type(<return_value>[0])=int
        ctypes.sizeof(<return_value>)= ctypes.sizeof(element_type)*len(<return_value>)

    element_type=c_char,
        type(<return_value>)=?,
        type(<return_value>[0])=str
        ctypes.sizeof(<return_value>)= ctypes.sizeof(element_type)*len(<return_value>)

    '''
    sz = addr_size / ctypes.sizeof(element_type)
    return (element_type * sz).from_address(addr)


def ctypes_array_as_array(old_array, new_array_element_type):
    bytes_size = ctypes.sizeof(old_array)
    return ctypes_addr_as_array(ctypes.addressof(old_array)
                                , bytes_size
                                , new_array_element_type
                                )

def RtnHrFuncType(*args, **kwargs):
    return ExportFuncType(c_int,*args,**kwargs)

class CppExportStructure(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('cb', c_uint),
        ('pfn_func_empty', RtnHrFuncType()),
        ('pfn_func_change_value_int', RtnHrFuncType(POINTER(c_uint))),
        ('pfn_func_in_memory', RtnHrFuncType(c_char_p, c_uint)),
        ('pfn_func_in_memoryw', RtnHrFuncType(c_wchar_p, c_uint)),
        ('pfn_func_out_memory_noalloc', RtnHrFuncType(POINTER(c_void_p), POINTER(c_uint))),
        ('pfn_func_out_memory_alloc', RtnHrFuncType(c_void_p, POINTER(c_uint))),
        ('pfn_func_address_read', RtnHrFuncType(POINTER(c_void_p), POINTER(c_uint))),
    ]

    def __init__(self, *args, **kwargs):
        super(CppExportStructure, self).__init__(*args, **kwargs)
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
        # Way 1:
        # addr = ctypes_api_bytes_string_addr(bytes_string)
        # 非必须
        # addr_size=ctypes.c_uint(len(bytes_string))
        # addr = ctypes.cast(addr, ctypes.c_char_p)

        # Way 2:
        addr = bytes_string
        hr = self.pfn_func_in_memory(addr, len(bytes_string))
        assert (hr == 0)
        return (hr,)

    def pass_python_unicode_string(self, unicode_string):
        ''' A wchar_t string value in python, pass it to cpp only for read
        '''

        # Can not use pystring_as_string_size
        # Way 1:
        addr_buffer = ctypes.create_unicode_buffer(unicode_string)
        # Way 2:
        # addr_buffer = unicode_string
        # Way 3:
        # addr_buffer = ctypes.c_wchar_p(unicode_string)
        # In Visual Studio, debug it, see the unicode is utf16(2 bytes)
        hr = self.pfn_func_in_memoryw(addr_buffer, len(unicode_string))
        assert (hr == 0)
        return (hr,)

    def pass_python_unicode_string2(self, ptr, size):
        '''
        :param ptr:  int
        :param size: int
        '''
        ptr = ctypes.cast(ptr, ctypes.c_wchar_p)
        hr = self.pfn_func_in_memoryw(ptr, size)
        assert (hr == 0)
        return (hr,)

    def out_memory_python_noalloc(self):
        '''return a memory address and size from cpp, only read in python'''

        addr = ctypes.c_void_p(0)
        addr_size = ctypes.c_uint(0)
        pfn = self.pfn_func_out_memory_noalloc
        hr = pfn(ctypes.pointer(addr), ctypes.pointer(addr_size))
        assert (hr == 0 and addr_size.value > 0)
        io_print(u'python_print->ctypes 从 cpp 返回的字符串内存地址 {0}'.format(
            hex(addr.value)
        ))
        vm = ctypes_addr_as_array(addr.value, addr_size.value, ctypes.c_ubyte)

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
        io_print(u'python_print->ctypes 提供申请的字符串内存地址 {0}'.format(
            hex(ctypes.addressof(addr))
        ))
        hr = pfn(addr, pointer(addr_size))
        assert (hr == 0)
        return (hr, addr.value)


    def address_read(self):
        import base64
        addr = ctypes.c_void_p(0)
        addr_size = ctypes.c_uint(0)
        pfn = self.pfn_func_address_read
        hr = pfn(ctypes.pointer(addr), ctypes.pointer(addr_size))
        assert (hr == 0 and addr_size.value > 0)
        io_print(u'python_print->从 cpp 返回的 addr={0} size={1}'.format(
            hex(addr.value),addr_size.value
        ))
        addr = addr.value
        addr_size=addr_size.value

        bytes_read = ctypes_addr_as_array(addr,addr_size,ctypes.c_ubyte)
        b1  =base64.b64encode(bytes_read)

        uints_read=ctypes_addr_as_array(addr,addr_size,ctypes.c_uint)
        b2 = base64.b64encode(uints_read)
        io_print(u'encode bytes {0}'.format(b1))
        io_print(u'encode uints {0}'.format(b2))
        assert (b1 == b2)