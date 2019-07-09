#!/bin/python3
# cython: language_level=3

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

ext_module = cythonize([Extension('cleanermaster',
                                  ['cleanermaster.pyx'],
                                  extra_compile_args=["--std=c++14"],
                                  extra_link_args=["--std=c++14"],
                                  language='c++',
                                  libraries=['rt', 'boost_thread'],
                                  # libraries_dirs=['/lib/x86_64-linux-gnu/']
                                  )], force=True)

for e in ext_module:
    e.cython_directives = {'embedsignature': True}

setup(
    name='Client to submit polygons to Engine',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_module
)
