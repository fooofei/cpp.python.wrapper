#!/bin/bash


# 失败就退出
mkdir build
cd build
cmake .. || exit 1
make  || exit 1

cd ..
python  cpp_python_call.py|| exit 1
rm -rf build