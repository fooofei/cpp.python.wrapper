
## C++ 与 Python 粘合最好的实践方法 [![Build Status](https://travis-ci.org/fooofei/cpp_python_wrapper.svg?branch=master)](https://travis-ci.org/fooofei/cpp_python_wrapper)

对比过 Cython(可以写 C++ class), Python COM, swig， 此方法是最好的。

ctypes 兼容性好。C++ 模块 与 Python中结构定义 两者间新老版本搭配完全无风险。

增加了 cffi 使用对比 ctypes。

## 项目说明

Windows 使用 stdcall

linux/unix 使用 cdecl

## 测试

1 install cmake

2 run direct_run.bat on Windows, run direct_run.sh on linux/unix

3 see output


## platforms

python2

win32, linux, macOS


clear.py 不再使用