@echo off

%~d0
cd /d %~dp0



:: ����д�����˳�
cmake -G "Visual Studio 11 2012" . || exit /B 1 
cmake --build . || exit /B 1
python python_caller.py || exit /B 1
python clear.py || exit /B 1