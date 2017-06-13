# coding=utf-8

'''
cffi  have two types: cdata and buffer

c api not accept buffer, but only cdata.
 TypeError: initializer for ctype 'void *' must be a cdata pointer, not _cffi_backend.buffer

'''

import unittest
import cffi
import ctypes

ffi = cffi.FFI()


def ctypes_api_bytes_string_addr(v):
    f = ctypes.pythonapi.PyString_AsString
    f.restype = ctypes.c_void_p
    f.argtypes = [ctypes.py_object]
    return f(v)


def cffi_bytes_string_int_address(v):
    return int(cffi_bytes_string_cdata_address(v))


def cffi_bytes_string_cdata_address(v):
    r = ffi.from_buffer(v)
    r = ffi.cast('uintptr_t', r)
    return r


def int_address_to_string(addr, length):
    '''
    int, <cdata of uintptr_t> in ffi.string all wrong type
    '''

    addr = ffi.cast('const char *', addr)
    return ffi.string(addr, length)

def int_address_to_string_2(addr, length):
    '''
    I like the ffi.buffer(), it can do same work with ffi.string()
    '''
    addr = ffi.cast('const char *', addr)
    return ffi.buffer(addr, length)[:]


class MyTestCase(unittest.TestCase):
    def test_address(self):
        a = 'helloworld'
        addr1 = ctypes_api_bytes_string_addr(a)
        addr2 = cffi_bytes_string_cdata_address(a)
        self.assertEqual(addr1, addr2)

    def test_address_to_bytes_string_1(self):
        a = 'helloworld'

        addr_int = cffi_bytes_string_int_address(a)
        self.assertIsInstance(addr_int, long)

        v = int_address_to_string(addr_int, len(a))

        self.assertEqual(v, a)

        addr_int2 = cffi_bytes_string_cdata_address(v)
        self.assertNotEqual(addr_int2, addr_int)

    def test_address_to_bytes_string_2(self):
        a = 'helloworld'

        addr_int = cffi_bytes_string_int_address(a)
        self.assertIsInstance(addr_int, long)

        v = int_address_to_string_2(addr_int, len(a))

        self.assertEqual(v, a)

        addr_int2 = cffi_bytes_string_cdata_address(v)
        self.assertNotEqual(addr_int2, addr_int)

    def test_unpack_interger_array_1(self):
        a = b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x04\x00\x00'
        self.assertEqual(12, len(a))

        self.assertEqual(3 * ffi.sizeof('unsigned'), len(a))

        addr_int = cffi_bytes_string_int_address(a)

        addr_unsigned_p = ffi.cast('const unsigned *', addr_int)


        v = ffi.unpack(addr_unsigned_p, len(a)/ffi.sizeof('unsigned'))
        self.assertEqual(v[0],1)
        self.assertEqual(v[1],2)
        self.assertEqual(v[2],0x0403)

    def test_unpack_interger_array_2(self):
        a = b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x04\x00\x00'
        self.assertEqual(12, len(a))

        self.assertEqual(6 * ffi.sizeof('unsigned short'), len(a))

        addr_int = cffi_bytes_string_int_address(a)

        addr_unsigned_p = ffi.cast('const unsigned short *', addr_int)

        v = ffi.unpack(addr_unsigned_p, len(a)/ffi.sizeof('unsigned short'))
        self.assertEqual(v[0],1)
        self.assertEqual(v[1],0)
        self.assertEqual(v[2],2)
        self.assertEqual(v[4], 0x0403)


    def test_buffer_length(self):
        '''
        All buffer length is the  length of buffer(cast('const char *') )
        '''
        a = b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x04\x00\x00'
        self.assertEqual(12, len(a))

        addr = cffi_bytes_string_int_address(a)

        buf1 = ffi.buffer(ffi.cast('const char *',addr), len(a))

        self.assertEqual(12, len(buf1))

        buf2 = ffi.buffer(ffi.cast('const void *', addr), len(a))

        self.assertEqual(12, len(buf2))

        buf3 = ffi.buffer(ffi.cast('const unsigned *', addr), len(a))

        self.assertEqual(12, len(buf3))


    ''' api value type of  args or return '''

    def test_cffi_from_buffer_api(self):
        a = 'helloword'
        addr = ffi.from_buffer(a)
        self.assertIsInstance(addr, ffi.CData)



    def test_len_array(self):
        v = ffi.new('unsigned []', 4)
        self.assertEqual(len(v), 4)

    def test_len_array_2(self):
        v = ffi.new('unsigned short []', 10)
        self.assertEqual(len(v), 10)

    def test_sizeof_1(self):
        self.assertEqual(ffi.sizeof('unsigned'), 4)

    def test_sizeof_2(self):
        v = ffi.new('unsigned []', 4)
        self.assertEqual(ffi.sizeof(v), 4*4)

    def test_sizeof_3(self):
        v = ffi.new('unsigned short []', 10)
        self.assertEqual(ffi.sizeof(v), 10*2)



    def test_address_to_bytes_string_error_1(self):
        ''' TypeError: string() argument 1 must be _cffi_backend.CData, not int '''
        with self.assertRaises(TypeError):
            a = 'helloworld'
            addr = ctypes_api_bytes_string_addr(a)
            v = ffi.string(addr, len(a))

    def test_address_to_bytes_string_error_2(self):
        with self.assertRaises(TypeError):
            a = 'helloworld'
            addr = cffi_bytes_string_int_address(a)
            v = ffi.string(addr, len(a))

    def test_new_cdata_1(self):
        a = ffi.new('char[]', 'hello')
        self.assertEqual(len(a), 6)
        self.assertIsInstance(a, ffi.CData)

    '''  memory allocs test  '''

    def test_buffer_api_not_alloc(self):
        a = 'helloworld'
        addr = ffi.from_buffer(a)
        self.assertIsInstance(addr, ffi.CData)

        buf = ffi.buffer(addr, len(a))
        self.assertIsInstance(buf, ffi.buffer)

        self.assertEqual(a, buf[:])

    def test_from_buffer_api_not_alloc(self):
        '''
        bytes string -> cffi cdata address  (no memory alloc)

        '''
        a = 'helloword'

        addr = ffi.from_buffer(a)

        self.assertIsInstance(addr, ffi.CData)

        addr_int = ffi.cast('const void *', addr)
        self.assertIsInstance(addr_int, ffi.CData)

        addr_int = ffi.cast('uintptr_t', addr_int)
        self.assertIsInstance(addr_int, ffi.CData)
        addr_int = int(addr_int)

        self.assertEqual(cffi_bytes_string_int_address(a),
                         addr_int)

    def test_cffi_string_api_alloced(self):
        a = 'helloworld'

        addr = cffi_bytes_string_int_address(a)

        v = int_address_to_string(addr, len(a))
        self.assertIsInstance(v, str)

        addr1 = cffi_bytes_string_int_address(a)
        addr2 = cffi_bytes_string_cdata_address(v)

        self.assertNotEqual(addr1, addr2)

    ''''''


if __name__ == '__main__':
    unittest.main()
