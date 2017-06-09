@echo off

%~d0
cd /d %~dp0



:: 如果有错误就退出
mkdir build
cd build
cmake -G "Visual Studio 11 2012" .. || exit /B 1 
cmake --build . --config Release || exit /B 1
::xcopy Release\cpp_python.dll .. /Y
cd ..
python cpp_python_test.py || exit /B 1
rmdir /S /Q build