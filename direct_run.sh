#!/bin/bash


# 失败就退出
mkdir build
cd build
cmake .. || exit 1
make  || exit 1
cp libcpp_python.so ..
cd ..
python  python_caller.py|| exit 1
rm -rf build
#python clear.py