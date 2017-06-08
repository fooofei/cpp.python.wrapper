
## C++ 与 Python 粘合最好的实践方法

对比过 Cython(可以写 c++ class), Python COM, swig， 此方法是最好的。

兼容性好。C++ 模块 与 Python中结构定义 两者间新老版本搭配完全无风险。


## 项目说明

Windows 使用 stdcall

Linux 使用 cdecl

## 测试

1. install cmake

2. run direct_run.bat on Windows, run direct_run.sh on *unix 

3. see output

one output in linux
```
$  bash direct_run.sh
-- The C compiler identification is GNU 5.4.0
-- The CXX compiler identification is GNU 5.4.0
-- Check for working C compiler: /usr/bin/cc
-- Check for working C compiler: /usr/bin/cc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting C compile features
-- Detecting C compile features - done
-- Check for working CXX compiler: /usr/bin/c++
-- Check for working CXX compiler: /usr/bin/c++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Configuring done
-- Generating done
-- Build files have been written to: /home/a/f/everysamples/0000/bbs/cpp_python_wrapper
Scanning dependencies of target cpp_python
[ 50%] Building CXX object CMakeFiles/cpp_python.dir/cpp_functions.cpp.o
[100%] Linking CXX shared library libcpp_python.so
[100%] Built target cpp_python
call func_empty()
test_func_change_value_int: 0->110
print from cpp->size:(44),value:(this is string in python test_func_in_memory)
print from cpp->size:(45),value:(this is string in python test_func_in_memoryw)
out string from cpp in func_out_memory_noalloc
out string from cpp in func_out_memory_alloc
```

clear.py 不再使用