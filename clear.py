#coding=utf-8
from __future__ import unicode_literals

import os
import sys

curpath = os.path.dirname(os.path.realpath(__file__))

def remove_empty_folder(dst):
    '''
    删除 dst 内部的所有空目录
    '''
    rms = []
    for root, subs, files in os.walk(dst):
        for e in subs:
            rms.append(os.path.join(root,e))
    # 列表倒序 就可以省去递归 省去删除非空文件夹的事情
    for e in rms[::-1]:
        if not os.listdir(e):
            os.rmdir(e)


def entry():
    files_not_delete = ['clear.py',
                        'cmakelists.txt',
                        'cpp_functions.h',
                        'cpp_functions.cpp',
                        'io_in_out.py',
                        'python_caller.py',
                        #'cpp_python.dll',
                        #'libcpp_python.so',
                        'direct_run.bat',
                        'direct_run.sh']

    def not_in(fullpath):
        fullpath = fullpath.lower()
        for e in files_not_delete:
            if fullpath.endswith(e):
                return False
        return True

    for root,subs,files in os.walk(curpath):
        for file in files :
            fullpath = os.path.join(root,file)
            if not_in(fullpath):
                os.remove(fullpath)

    remove_empty_folder(curpath)


if __name__ == '__main__':
    entry()