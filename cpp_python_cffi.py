# coding=utf-8


import io_in_out
from io_in_out import io_print


class CffiExportStructure(object):
    '''
    http://cffi.readthedocs.io/en/latest/ref.html#ffi-buffer-ffi-from-buffer
    官方文档只说了 ffi.buffer(cdata, [size]) 不申请内存，
    我测试 ffi.string(cdata, [maxlen]) 重新申请了内存,
    ffi.new(cdecl, init=None) 申请内存.

    ffi.from_buffer(python_buffer)  python string -> raw C data
    ffi.buffer(cdata, [size])  raw C data -> cffi buffer
         # 该函数没申请内存 是 buffer 实例，如果要申请内存变为 str 实例，则 <return_value>[:], 实测地址会变
    ffi.string(cdata, [maxlen]) raw C data -> python string

    cpp 中的结构体对齐方式是 1，在 cffi 中无效
    #pragma pack(push,1)

    '''

    def __init__(self, fullpath_dll):
        self._cffi_ins = None
        self._c_export_functions = None

        self._cffi_init(fullpath_dll)

    @property
    def valid(self):
        return self._cffi_ins is not None and self._c_export_functions is not None

    def _cffi_init(self, fullpath_dll):
        import cffi
        ffi = cffi.FFI()

        print ('cffi version :{}'.format(cffi.__version_info__))

        ffi.cdef(
            '''
    
    typedef struct 
    {
        unsigned int cb;
        int (WINAPI * pfn_func_empty)();
        int (WINAPI * pfn_func_change_value_int)(unsigned int * pvalue);
        int (WINAPI * pfn_func_in_memory)(const char * ptr, unsigned int ptr_size);
        int (WINAPI * pfn_func_in_memoryw)(const wchar_t * ptr, unsigned int ptr_size);
        int (WINAPI * pfn_func_out_memory_noalloc)(const void ** out_ptr, unsigned int * out_ptr_size);
        int (WINAPI * pfn_func_out_memory_alloc)(void * out_ptr, unsigned int * out_ptr_size);
    }ExportFunctions;
      int WINAPI InitExportFunctions(ExportFunctions *);
    '''
            , packed=True)

        io_print(u'load {}'.format(fullpath_dll))
        cpp_python = ffi.dlopen(fullpath_dll)

        c_export_functions = ffi.new('ExportFunctions *')
        # c_export_functions = ffi.new('ExportFunctions []',1)
        c_export_functions_size = ffi.sizeof(c_export_functions[0])
        c_export_functions[0].cb = c_export_functions_size

        c_return = cpp_python.InitExportFunctions(c_export_functions)
        assert (c_export_functions.cb == c_export_functions_size)
        if c_return == 0:
            self._c_export_functions = c_export_functions
            self._cffi_ins = ffi

    def empty(self):
        hr = self._c_export_functions.pfn_func_empty()
        assert hr == 0
        return (hr,)

    def change_value_int(self, value):
        '''
        If not use cffi new, will raise Error :
                TypeError: initializer for ctype 'unsigned int *' must be a cdata pointer, not int
        '''
        c_value_int = self._cffi_ins.new('unsigned *', value)
        hr = self._c_export_functions.pfn_func_change_value_int(c_value_int)
        assert hr == 0
        # 取值就是在后面加 <ins>[0] , 与 ctypes 取值是 <ins>.value 不同
        return (hr, c_value_int[0])

    def pass_python_bytes_string(self, bytes_string):
        ''' python 中的内存给 cpp 读'''

        if not isinstance(bytes_string, io_in_out.io_binary_type):
            raise ValueError('must be type {}'.format(io_in_out.io_binary_type))

        # 用不用这个没关系
        # c_value_c_char_p = self._cffi_ins.from_buffer(value)
        hr = self._c_export_functions.pfn_func_in_memory(bytes_string, len(bytes_string))
        assert hr == 0
        return (hr,)

    def pass_python_unicode_string(self, unicode_string):
        '''存在内存拷贝（ctypes 获取的地址与 cpp 中读到的不一致 两边不知道谁错了）'''
        if not isinstance(unicode_string, io_in_out.io_text_type):
            raise ValueError('must be type {}'.format(io_in_out.io_text_type))
        hr = self._c_export_functions.pfn_func_in_memoryw(unicode_string, len(unicode_string))
        assert hr == 0
        return (hr,)

    def pass_python_unicode_string2(self, ptr, len_):
        '''
        直接传递内存地址（尝试失败了）
        '''
        hr = self._c_export_functions.pfn_func_in_memoryw(ptr, len_)
        assert hr == 0
        return (hr,)

    def out_memory_python_noalloc(self):
        ptr = self._cffi_ins.new('const void **')
        size = self._cffi_ins.new('unsigned *')
        hr = self._c_export_functions.pfn_func_out_memory_noalloc(ptr, size)
        assert (hr == 0)

        io_print(u'python_print->从 cpp 返回的字符串内存地址 {}'.format(ptr[0]))
        value = self._cffi_ins.buffer(ptr[0], size[0])

        # value2 = value[:] # 这样是生成了新的字符串
        return (hr, value)

    def out_memory_python_alloc(self):
        size = self._cffi_ins.new('unsigned *')
        pfn = self._c_export_functions.pfn_func_out_memory_alloc
        hr = pfn(self._cffi_ins.NULL, size)
        if hr == 0 and size[0] > 0:
            ptr = self._cffi_ins.new('unsigned char[]', size[0])
            io_print(u'python_print->cffi 提供申请的字符串内存地址 {}'.format(self._cffi_ins.addressof(ptr)[0]))
            hr = pfn(ptr, size)
            if hr == 0 and size[0] > 0:
                # not use ptr[0]
                value = self._cffi_ins.buffer(ptr, size[0])
                return (hr, value)
        assert (hr == 0)
        return (hr, None)

    def test_func_not_exist_in_cffi(self):
        '''
        AttributeError: cdata 'ExportFunctions *' has no field 'func_not_exists'
        '''
        hr = self._c_export_functions.func_not_exists()
