#!/bin/bash

#Script that compiles the C++ scanline algorithm with cython to a python module and copies it into the current folder
#If there is an __init__.py in the folder the setup script will create subfolders, so avoid that
cd "$(dirname "$0")"
cd source

echo pwd

DRCDIR="../../python/kppc/drc/"

python3 setup.py build_ext -b $DRCDIR &
python3 setup_cc.py build_ext -b $DRCDIR &
g++ CleanerMain.cpp CleanerSlave.cpp DrcSl.cpp SignalHandler.cpp -o $DRCDIR/cleanermain -isystem /usr/include/boost/ -lboost_system -pthread -lboost_thread -lrt

#/usr/bin/python3 setup.py build_ext -b ./
#cp slcleaner.cpython* ../

