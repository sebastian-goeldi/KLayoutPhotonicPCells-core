#!/bin/bash

#Script that compiles the C++ scanline algorithm with cython to a python module and copies it into the current folder
#If there is an __init__.py in the folder the setup script will create subfolders, so avoid that
cd "$(dirname "$0")"
cd slcleaner_source
python3 setup.py build_ext -b ./
/usr/bin/python3 setup.py build_ext -b ./
cp slcleaner.cpython* ../
