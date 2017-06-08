cmake_minimum_required (VERSION 2.6)
project (cpp_python)
message(STATUS "cpp_python_SOURCE_DIR=" ${cpp_python_SOURCE_DIR})
message(STATUS "cpp_python_BINARY_DIR" ${cpp_python_BINARY_DIR})

# Apple's Warning
# https://stackoverflow.com/questions/31561309/cmake-warnings-under-os-x-macosx-rpath-is-not-specified-for-the-following-targe
if (APPLE)
    set(CMAKE_MACOSX_RPATH 0)
endif ()

# 此标记用于当 add_library 中无 STATIC/SHARED 显式声明时使用
# https://cmake.org/cmake/help/v3.0/command/add_library.html#command:add_library
#set (BUILD_SHARED_LIBS ON)

add_library(cpp_python SHARED cpp_functions.cpp)

add_custom_command(
        TARGET cpp_python POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:cpp_python> ../$<TARGET_FILE_NAME:cpp_python>
)