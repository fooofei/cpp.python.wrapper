# coding=utf-8

'''
总结 ctypes 和 cffi  :
 1 bytes string 都能无 copy 的从 python 传递给 cpp
    其中 cffi 传递起来更简单

 2 unicode string 都没办法无 copy 传递
    cffi 无办法获取 unicode string 地址
    ctypes 获取到的地址还无法验证是否正确 因为传递给 cpp 的是另一个地址

 3 读取 cpp 中提供的地址 或者创建内存提供给 cpp 写
    都是 cffi 简单

'''

import os
import sys
import ctypes
from  io_in_out import io_print
import cffi

curpath = os.path.dirname(os.path.realpath(__file__))

from cpp_python_ctypes import bytes_string_address
from cpp_python_ctypes import bytes_string_address2
from cpp_python_ctypes import text_string_address

ffi = cffi.FFI()

cffi_address_of = lambda v: ffi.addressof(ffi.from_buffer(v))


def c_bytes_string_address(v):
    if sys.platform.startswith('win32'):
        import string_address
        r = string_address.PyString_AddressSize(v)
        assert (r)
        assert (r[1] == len(v))
        io_print(u'python_print->address by c {}'.format(hex(r[0])))

def c_unicode_string_address(v):
    if sys.platform.startswith('win32'):
        import string_address
        r = string_address.PyUnicodeString_AddressSize(v)
        assert (r)
        assert (r[1] == len(v)*ctypes.sizeof(ctypes.c_wchar))
        io_print(u'python_print->address by c {}'.format(hex(r[0])))


def change_value_int(ins):
    io_print(u'test_func_change_value_int')
    v = 2
    io_print(u'python_python->pass value {} to cpp'.format(v))
    r = ins.change_value_int(v)
    io_print(u'python_python->return value from cpp {}'.format(r[1]))
    io_print('')


def pass_python_bytes_string(ins):
    ##
    io_print(u'test_func_pass_python_bytes_string')
    v = 'this is string in python pass_python_bytes_string'

    cffi_addr = cffi_address_of(v)
    io_print(u'python_print->address by cffi {}'.format(cffi_addr[0]))

    ctypes_addr = bytes_string_address(v)
    io_print(u'python_print->address by ctypes bytes_string_address {}'.format(hex(ctypes_addr.value)))

    ctypes_addr2 = bytes_string_address2(v)
    io_print(u'python_print->address by ctypes bytes_string_address2 {}'.format(hex(ctypes_addr2.value)))

    c_bytes_string_address(v)

    # check
    x = ffi.cast('void*', ctypes_addr.value)
    assert (cffi_addr == x)
    assert (v == ffi.buffer(cffi_addr, len(v)) == ctypes.string_at(ctypes_addr, len(v)))

    io_print('python_print->pass bytes string to cpp [{}]{}'.format(len(v), v))
    r = ins.pass_python_bytes_string(v)
    io_print('')


def pass_python_unicode_string(ins):
    ##
    io_print(u'test_func_pass_python_unicode_string')
    v = u'this is string in python pass_python_unicode_string'
    io_print(u'python_print->pass unicode string to cpp [{}]{}'.format(len(v), v))
    io_print(u'现在还没有办法用 cffi 获取 unicode string 的字符串地址')

    io_print(u'ctypes 中获取的地址在 macOS 中也不对')
    io_print(u'别强求了 unicodestring 不应该包裹大内存')
    io_print(u'看来即使是文件路径的字符串也无法避免拷贝内存了')
    ctypes_addr1 = bytes_string_address(v)
    io_print(u'python_print->address by ctypes bytes_string_address {}'.format(hex(ctypes_addr1.value)))

    ctypes_addr = text_string_address(v)
    io_print(u'python_print->address by ctypes text_string_address {}'.format(hex(ctypes_addr.value)))

    c_unicode_string_address(v)

    # 逆向操作 再次读取 检查值相等
    # x = ctypes.wstring_at(ctypes_addr, len(v))
    # assert (x == v)

    # TODO not right on none_Windows platform
    r = ins.pass_python_unicode_string2(ctypes_addr.value, len(v))
    #r = ins.pass_python_unicode_string(v)
    io_print('')

    ##
    io_print(u'test_func_pass_python_unicode_string_chs')
    v = u'这是来自 Python 的字符串，用中文表示，长度27'
    io_print(u'python_print->pass unicode string to cpp [{}]{}'.format(len(v), v))
    ctypes_addr = text_string_address(v)
    io_print(u'python_print->address by ctypes text_string_address {}'.format(hex(ctypes_addr.value)))

    c_unicode_string_address(v)

    # x = ctypes.wstring_at(ctypes_addr, len(v))
    # assert (x == v)
    #r = ins.pass_python_unicode_string(v)
    r = ins.pass_python_unicode_string2(ctypes_addr.value,len(v))
    io_print('')


def out_memory_python_noalloc(ins):
    ##
    io_print(u'test_func_out_memory_python_noalloc')
    r = ins.out_memory_python_noalloc()
    io_print(u'python_print->out memory [{}]{}'.format(len(r[1]), r[1]))

    cffi_addr = cffi_address_of(r[1])
    io_print(u'python_print->这里有字符串内存拷贝')
    io_print(u'python_print->address result by cffi {}'.format(cffi_addr[0]))

    io_print('')


def out_memory_python_alloc(ins):
    ##
    io_print(u'test_func_out_memory_python_alloc')
    r = ins.out_memory_python_alloc()
    io_print(u'python_print->out memory [{}]{}'.format(len(r[1]), r[1]))
    io_print('')


def cpp_python_framework(ins):
    # ffi 的 cast 就不能把 string 转换


    ##
    io_print('test_func_empty')
    ins.empty()
    io_print('')

    change_value_int(ins)
    pass_python_bytes_string(ins)
    pass_python_unicode_string(ins)
    out_memory_python_noalloc(ins)
    out_memory_python_alloc(ins)


def entry():
    from cpp_python_cffi import CffiExportStructure
    from cpp_python_ctypes import CppExportStructure

    a = {u'win32': u'cpp_python.dll',
         u'linux': u'libcpp_python.so',
         u'darwin': u'libcpp_python.dylib'}
    n = filter(sys.platform.startswith, a.keys())
    assert (len(n) == 1)
    n = a.get(n[0])
    if not n:
        raise ValueError('not found right name')

    p = os.path.join(curpath, n)
    # p = os.path.join(curpath,u'cmake-build-debug',u'libcpp_python.dylib')
    # p = r'D:\Visual_Studio_Projects\cpp_python_vs\Debug\cpp_python_vs.dll'


    ins = CffiExportStructure(p)
    assert (ins.valid)
    cpp_python_framework(ins)

    ins = CppExportStructure()
    ins.loadlib(p)
    cpp_python_framework(ins)


if __name__ == '__main__':
    entry()
