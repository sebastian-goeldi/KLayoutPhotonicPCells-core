#!/bin/python3
#cython: language_level=3

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

ext_module = [Extension('slcleaner',
                        ['slcleaner.pyx'],
                        extra_compile_args=["--std=c++14"],
                        extra_link_args=["--std=c++14"],
                        language='c++')]

for e in ext_module:
	e.cython_directives = {'embedsignature': True}

setup(
	name='Design Rule Cleaner based on Scanline Algorithm',
	cmdclass={'build_ext': build_ext},
	ext_modules=ext_module
)