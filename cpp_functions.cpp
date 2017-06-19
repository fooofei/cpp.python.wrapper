
#include "cpp_functions.h"

#include <iostream>
#include <string>
#include <algorithm>

// Also can use HRESULT to replace.
enum 
{ 
    E_NO_ERROR =0,
    E_ERROR_ARG,
    E_ERROR_FAIL,
    E_ERROR_NOIMPL,
};

#define RASSERT_RETURN(exp, r) \
    do\
    {\
        if(!(exp)) {return (r);}\
    }while(0);


extern "C"
int WINAPI InitExportFunctions(ExportFunctions * arg)
{
    RASSERT_RETURN(arg, E_ERROR_ARG);

    unsigned int cb;
    const unsigned int version_1_function_count = 6; 
    // step 1 Increment here.
    const unsigned int version_2_functon_count = 7;
    const unsigned int version_3_functon_count = 8;
    unsigned int func_count ;

    cb = arg->cb;
    if((cb<=0)) {
        return  E_ERROR_ARG;
    }
    cb -= 4;

    RASSERT_RETURN(cb%sizeof(void*)==0,E_ERROR_ARG);
    func_count = cb/sizeof(void*);

    // step 2 Increment here
    // conflict  std::min  min
    // (std::min)<unsigned> Visual Studio 2017 compile error
    // but not (std::min<unsigned>) 
    func_count = std::min<unsigned>(func_count, version_3_functon_count);

    switch (func_count)
    {
        // step 3
        case version_3_functon_count:
            arg->pfn_func_out_memoryw = func_out_memoryw;
        case version_2_functon_count:
            arg->pfn_func_address_read=func_address_read;
            // not break out
        case version_1_function_count:
            arg->pfn_func_change_value_int = func_change_value_int;
            arg->pfn_func_empty = func_empty;
            arg->pfn_func_in_memory = func_in_memory;
            arg->pfn_func_in_memoryw = func_in_memoryw;
            arg->pfn_func_out_memory_noalloc = func_out_memory_noalloc;
            arg->pfn_func_out_memory_alloc = func_out_memory_alloc;
            // return the real size.
            arg->cb = 4 + func_count * sizeof(void*);
            return E_NO_ERROR;
        default:
            break;
    }
    return E_ERROR_NOIMPL;

}


int WINAPI func_empty()
{
    printf("cpp_print->[len:36]call func_empty()\n");
    fflush(stdout);
    return E_NO_ERROR;
}

int WINAPI func_change_value_int(unsigned int * pvalue)
{
    RASSERT_RETURN(pvalue,E_ERROR_ARG);
    printf("cpp_print->get value int from python [%u], change to 110.\n",*pvalue);
    fflush(stdout);
    *pvalue = 110;
    return E_NO_ERROR;
}

int WINAPI func_in_memory(const char * ptr, unsigned int size)
{
    RASSERT_RETURN(ptr,E_ERROR_ARG);
    printf("cpp_print->memory from python [0x%p][%u]value:(%.*s)\n",(const void*)ptr,size,(int)size,ptr);
    fflush(stdout);
    return E_NO_ERROR;
}

void print_hex(const void * ptr, size_t l)
{
    printf("hex value: ");
    const unsigned char * p = (const unsigned char *)ptr;
    for (size_t i=0;i<l;++i)
    {
        printf("%02x ", *(p + i));
    }
    printf("\n");
    fflush(stdout);
}


int WINAPI func_in_memoryw(const wchar_t * ptr, unsigned int size)
{
    RASSERT_RETURN(ptr,E_ERROR_ARG);
    #ifdef WIN32
        const char * local = "chs";
    #else
        const char * local = "zh_CN.UTF-8";
    #endif

    print_hex(ptr, size * sizeof(wchar_t));

    char * restore = setlocale(LC_ALL,local);
    unsigned p_size = size*sizeof(wchar_t); // TODO ?

    printf("cpp_print->[0x%p][%u]value:(%.*ls)\n",(const void*)ptr,size,p_size,ptr);



    setlocale(LC_ALL, restore);
    fflush(stdout);
    return E_NO_ERROR;
}

int WINAPI func_out_memory_alloc(void * out_ptr, unsigned int * out_ptr_size)
{
    const char * p = "out string from cpp in func_out_memory_alloc";
    RASSERT_RETURN(out_ptr_size, E_ERROR_ARG);
    unsigned int l = (unsigned int)strlen(p);

    printf("cpp_print->out string [%u],%s\n", l, p);
    printf("cpp_print->get args [addr:0x%p],[size:%u]\n",out_ptr,*out_ptr_size);
    fflush(stdout);

    if (out_ptr)
    {
        if(!(l<*out_ptr_size))
        {
            *out_ptr_size = l+1;
            return E_ERROR_ARG;
        }
        memcpy(out_ptr,p,l);
    }
    else
    {
        *out_ptr_size = l+1;
    }
    return E_NO_ERROR;
}

static const char  g_p[] = "out string from cpp in func_out_memory_noalloc";

int WINAPI func_out_memory_noalloc(const void ** out_ptr, unsigned int * out_ptr_size)
{
    
    RASSERT_RETURN(out_ptr && out_ptr_size, E_ERROR_ARG);
    const char * p = g_p;
    unsigned int l = (unsigned int)strlen(p);

    printf("cpp_print->out string [%u],%s\n", l, p);
    printf("cpp_print->return [addr:0x%p],[size:%u]\n", (const void *)p, l);
    fflush(stdout);

    *out_ptr = p;
    *out_ptr_size = l;
    return E_NO_ERROR;
}

static const char g_alignment_memory[]= "aaaaaaaabbbbbbbbccccccccdddddddd";
int WINAPI func_address_read(const void ** out, unsigned  * out_size)
{
    RASSERT_RETURN(out && out_size, E_ERROR_ARG);

    const void * p = g_alignment_memory;
    unsigned size=(unsigned)strlen((const char *)p);
    printf("cpp_print->return [addr:0x%p],[size:%u]\n",p,size);
    fflush(stdout);

    *out=p;
    *out_size=size;

    return E_NO_ERROR;
}

int WINAPI func_out_memoryw(wchar_t * out, unsigned * out_size)
{
    RASSERT_RETURN(out_size, E_ERROR_ARG);

    wchar_t ch1 = 0x4f60;// ni
    wchar_t ch2 = 0x597d;// hao
    wchar_t ch3 = 0x6765;// lai
    wchar_t ch4 = 0x81ea;// zi

    std::wstring s;

    s.append(1, ch1);
    s.append(1, ch2);
    s.append(1, L',');
    s.append(1, ch3);
    s.append(1, ch4);
    s.append(L"cpp.");

    unsigned sz = (unsigned)s.size();

    if (out)
    {
        if (!(sz < *out_size))
        {
            *out_size = sz + 1;
            return E_ERROR_ARG;
        }
        printf("cpp_print->return [addr:0x%p],[size:%u]\n", out, sz);
        memcpy(out, s.c_str(), sizeof(wchar_t)*sz);
    }
    else
    {
        *out_size = sz + 1;
    }
    return E_NO_ERROR;

}