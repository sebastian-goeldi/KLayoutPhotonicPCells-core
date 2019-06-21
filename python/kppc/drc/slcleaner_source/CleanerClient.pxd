# distutils: language=c++

from libcpp.vector cimport vector

cdef extern from "CleanerClient.cpp":
    pass

cdef extern from "CleanerClient.h" namespace "drclean":
    cdef cppclass CleanerClient:
        CleanerClient() except +
        CleanerClient(int nlayers) except +

        int set_box(int layer, int datatype, int violation_width, int violation_space, int x1, int x2, int y1, int y2)
        void add_edge(int x1, int x2, int y1, int y2)
        int done()
        vector[vector[int]] get_layer()
