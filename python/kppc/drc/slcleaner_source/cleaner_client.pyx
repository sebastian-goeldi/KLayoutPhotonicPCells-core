# distutils: language=c++
# cython: language_level=3

from CleanerClient cimport CleanerClient
from DrcSl cimport DrcSl
import numpy as np

# from DrcSl cimport edgecoord

from libcpp cimport bool
from libcpp.vector cimport vector

cdef class PyCleanerClient:
    cdef CleanerClient c_cc

    def __cint__(self):
        self.c_cc = CleanerClient()

    def set_box(self, layer : int, datatype : int, violation_width : int, violation_space : int, x1 : int, x2 : int,
                y1 : int, y2 : int):
        self.c_cc.set_box(layer, datatype, violation_width, violation_space, x1, x2, y1, y2)

    def add_edge(self, x1 : int, x2 : int, y1 : int, y2 : int):
        self.c_cc.add_edge(x1, x2, y1, y2)

    def done(self):
        self.c_cc.done()
