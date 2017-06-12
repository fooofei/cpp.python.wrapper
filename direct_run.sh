#!/bin/bash


# 失败就退出
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release  .. || exit 1
make  || exit 1

cd ..
rm -rf build
python  cpp_python_call.py|| exit 1
