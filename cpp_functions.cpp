
#include "cpp_functions.h"

#include <iostream>
#include <string.h>

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
    // 1.Increment here.
    //const unsigned int version_2_functon_count = ?; 
    unsigned int func_count ;

    cb = arg->cb;
    cb -= 4;

    RASSERT_RETURN(cb%sizeof(void*)==0,E_ERROR_ARG);
    func_count = cb/sizeof(void*);

    // 2.Increment here
    func_count = (std::min<unsigned int>)(func_count,version_1_function_count);

    switch (func_count)
    {
        // 3.
    //case version2:

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
    printf("call func_empty()");
    fflush(stdout);
    return E_NO_ERROR;
}

int WINAPI func_change_value_int(unsigned int * pvalue)
{
    RASSERT_RETURN(pvalue,E_ERROR_ARG);
    *pvalue = 110;
    return E_NO_ERROR;
}

int WINAPI func_in_memory(const char * ptr, unsigned int size)
{
    RASSERT_RETURN(ptr,E_ERROR_ARG);
    printf("print from cpp->size:(%d),value:(%.*s)",size,(int)size,ptr);
    fflush(stdout);
    return E_NO_ERROR;
}

int WINAPI func_in_memoryw(const wchar_t * ptr, unsigned int size)
{
    RASSERT_RETURN(ptr,E_ERROR_ARG);
#ifdef WIN32
    wprintf(L"print from cpp->size:(%d),value:(%.*s)",size,(int)size,ptr);
#else
    printf("print from cpp->size:(%d),value:(%.*ls)",size,(int)size,ptr);
#endif
    fflush(stdout);
    return E_NO_ERROR;
}

int WINAPI func_out_memory_alloc(void * out_ptr, unsigned int * out_ptr_size)
{
    const char * p = "out string from cpp in func_out_memory_alloc";
    RASSERT_RETURN(out_ptr_size, E_ERROR_ARG);
    unsigned int l = (unsigned int)strlen(p);

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

    *out_ptr = p;
    *out_ptr_size = l;
    return E_NO_ERROR;
}