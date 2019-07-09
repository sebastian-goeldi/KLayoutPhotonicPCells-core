# distutils: language=c++

from libcpp.vector cimport vector
from libcpp.pair cimport pair

cdef extern from "CleanerMaster.cpp":
    pass

cdef extern from "CleanerMaster.h" namespace "drclean":
    cdef cppclass CleanerMaster:
        CleanerMaster() except +
        CleanerMaster(int nlayers) except +

        int set_box(int layer, int datatype, int violation_width, int violation_space, int x1, int x2, int y1, int y2)
        void add_edge(int x1, int x2, int y1, int y2)
        int done()
        vector[vector[int]] get_layer()
        vector[vector[pair[int,int]]] get_polygons()
