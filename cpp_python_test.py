# coding=utf-8

import os
import sys
import ctypes
from  io_in_out import io_print
import cffi


curpath = os.path.dirname(os.path.realpath(__file__))

# cast 为 ctypes.c_char_p 无法打印整型的地址，会把字符串输出
bytes_string_address = lambda  v : ctypes.cast(v,ctypes.c_void_p)
bytes_string_address2 = lambda  v : ctypes.cast(ctypes.cast(v,ctypes.c_char_p),ctypes.c_void_p)

# 知道上面两个等价后 下面这个我们就放心使用了
text_string_address = lambda v : ctypes.cast(ctypes.cast(v,ctypes.c_wchar_p),ctypes.c_void_p)
ffi = cffi.FFI()

cffi_address_of = lambda v : ffi.addressof(ffi.from_buffer(v))


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

    ctypes_addr1 = bytes_string_address(v)
    io_print(u'python_print->address by ctypes bytes_string_address {}'.format(hex(ctypes_addr1.value)))

    ctypes_addr = text_string_address(v)
    io_print(u'python_print->address by ctypes text_string_address {}'.format(hex(ctypes_addr.value)))

    x = ctypes.wstring_at(ctypes_addr, len(v))
    assert (x == v)

    r = ins.pass_python_unicode_string(v)
    io_print('')

    ##
    io_print(u'test_func_pass_python_unicode_string_chs')
    v = u'这是来自 Python 的字符串，用中文表示，长度27'
    io_print(u'python_print->pass unicode string to cpp [{}]{}'.format(len(v), v))
    ctypes_addr = text_string_address(v)
    io_print(u'python_print->address by ctypes text_string_address {}'.format(hex(ctypes_addr.value)))

    x = ctypes.wstring_at(ctypes_addr, len(v))
    assert (x == v)
    r = ins.pass_python_unicode_string(v)
    io_print('')


def out_memory_python_noalloc(ins):
    ##
    io_print(u'test_func_out_memory_python_noalloc')
    r = ins.out_memory_python_noalloc()
    io_print(u'python_print->out memory [{}]{}'.format(len(r[1]), r[1]))

    cffi_addr = cffi_address_of(r[1])
    io_print(u'python_print->address by cffi {}'.format(cffi_addr[0]))


    io_print('')


def out_memory_python_alloc(ins):
    ##
    io_print(u'test_func_out_memory_python_alloc')
    r = ins.out_memory_python_alloc()
    io_print(u'python_print->out memory [{}]{}'.format(len(r[1]), r[1]))
    io_print('')


def cpp_python_test_framework(ins):

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

    ins = CffiExportStructure()
    assert (ins.valid)
    cpp_python_test_framework(ins)


if __name__ == '__main__':
    entry()
