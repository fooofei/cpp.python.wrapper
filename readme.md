
## C++ 与 Python 粘合最好的实践方法 [![Build Status](https://travis-ci.org/fooofei/cpp_python_wrapper.svg?branch=master)](https://travis-ci.org/fooofei/cpp_python_wrapper)

现有一个第三方的 C 库，目标将其提供给 Python 使用，允许对其 C 接口简单封装。

对比过 Cython(可以写 C++ class), Python COM, swig， 此方法是最好的。

此方法固定了导出函数，且有一定的隐蔽作用，增加接口只需要改变导出结构体的成员，

通过 cb 成员做新旧版本兼容。

增加了 cffi 使用对比 ctypes。


## ctypes 优于 cffi 的

ctypes 可以对一块内存地址使用 

unsigned char * /unsigned int * 读取，cffi 只能使用 unsigned char * 读。


## cffi 优于 ctypes 的


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


##

20180725 看到一个 Pythran
