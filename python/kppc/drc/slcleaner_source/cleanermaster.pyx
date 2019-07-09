# distutils: language=c++
# cython: language_level=3

from CleanerMaster cimport CleanerMaster
from libcpp.vector cimport vector
from libcpp.pair cimport pair

cdef extern from "<utility>" namespace "std" nogil:
    T move[T](T)

cdef class PyCleanerMaster:
    cdef CleanerMaster c_cc

    def __cint__(self, nlayers : int):
        self.c_cc = CleanerMaster(nlayers)

    def set_box(self, layer : int, datatype : int, violation_width : int, violation_space : int, x1 : int, x2 : int,
                y1 : int, y2 : int):
        return self.c_cc.set_box(layer, datatype, violation_width, violation_space, x1, x2, y1, y2)

    def add_edge(self, x1 : int, x2 : int, y1 : int, y2 : int):
        self.c_cc.add_edge(x1, x2, y1, y2)

    def done(self):
        return self.c_cc.done()

    def get_layer(self):
        # arr = np.array([[]], dtype=np.int)
        cdef vector[vector[int]] res
        res = move(self.c_cc.get_layer())
        return res

    def polygons(self):
        cdef vector[vector[pair[int,int]]] polygons
        polygons = move(self.c_cc.get_polygons())
        print(len(polygons))
        return polygons
