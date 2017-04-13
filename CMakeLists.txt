#cmake_minimum_required (VERSION 3.5.1)
project (cpp_python)
message(${cpp_python_SOURCE_DIR})
message(${cpp_python_BINARY_DIR})

# 此标记用于当 add_library 中无 STATIC/SHARED 显式声明时使用
# https://cmake.org/cmake/help/v3.0/command/add_library.html#command:add_library
set (BUILD_SHARED_LIBS ON)
add_library(cpp_python SHARED cpp_functions.cpp)