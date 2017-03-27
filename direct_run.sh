#!/bin/bash


# Ê§°Ü¾ÍÍË³ö
cmake . || exit 1
make  || exit 1
python  python_caller.py|| exit 1
python clear.py