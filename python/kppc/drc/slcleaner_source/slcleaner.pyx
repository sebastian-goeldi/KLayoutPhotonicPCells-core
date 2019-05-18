# This file is part of KLayout-photonics, an extension for Photonic Layouts in KLayout.
# Copyright (c) 2018, Sebastian Goeldi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

# distutils: language=c++
# cython: language_level=3

"""Hello.

"""


from DrcSl cimport DrcSl
import numpy as np

# from DrcSl cimport edgecoord

from libcpp cimport bool
from libcpp.vector cimport vector

cdef class PyDrcSl:
    cdef DrcSl c_sl

    def __cint__(self):
        self.c_sl = DrcSl()

    def add_data(self, x1: int, x2: int, y1: int, y2: int):
        """Insert data into the scanline cleaner. The data is an edge that will be manhattanised and cleaned.

        .. note :: edges should be added in such a way that the outwards face is left in the direction of p1 to p2. Klayout already does this nicely.

        :param x1: x position of p1 of the edge
        :param x2: y position of p1 of the edge
        :param y1: x position of p2 of the edge
        :param y2: y position of p2 of the edge
        """
        self.c_sl.add_data(x1, x2, y1, y2)

    def init_list(self, x1: int, x2: int, y1: int, y2: int, viospace: int, viowidth: int):
        """(Re-)Initialize the Cleaner. x1,2 and y1,2 define the bounding box of the cleaner.

        .. warning ::

        If data outside this bounding box is added through the add_data function a Segmentation Fault will
            most likely occur and the module (including Klayout) crashes.

        :param x1: left bound of box
        :param x2: right bound of box
        :param y1: bottom bound of box
        :param y2: top bound of box
        :param viospace: minimum space violation in database units
        :param viowidth: minimum width violation in database units
        """
        self.c_sl.initialize_list(x1, x2, y1, y2, viospace, viowidth)

    def sort(self):
        """Sort the data in ascending order
        """
        self.c_sl.sortlist()

    def clean(self, x: int = 10):
        """Clean data in the vector for space and width violations

        :param x: number of max tries
        """
        cdef int cx = x
        self.c_sl.clean(cx)

    def printvector(self, beg = -1, end = -1):
        """Print the data of rows/colums depending on current orientation

        :param beg: begining of the rows/columns that should be printed
        :param end: ending of the rows/columns that should be printed
        """
        self.c_sl.printvector(beg, end)

    def get_row(self, ind: int):
        """Get the edge data back to python from the C++ object.

        :param ind: index of the row to retrieve data from
        :return: numpy array of the edges
        """
        cdef vector[int] res
        res = self.c_sl.get_vect(ind)
        return np.array(res, dtype=int)

    def get_row_types(self, ind: int):
        """Get the type of edges in that row.

        :param ind: index of the row
        :return: numpy array of types of edges (0 for upwards facing edge, 1 for downwards)
        """
        cdef vector[int] res
        res = self.c_sl.get_types(ind)
        return np.array(res, dtype=int)

    def clean_space(self):
        """Clean the current data for space violations.
        """
        self.c_sl.clean_space()

    def clean_width(self):
        """Clean the current data for width violations.
        """
        self.c_sl.clean_width()

    def switch_dimensions(self):
        """Switch the orientation of the data. From row oriented to column oriented and vice-versa.
        """
        self.c_sl.switch_dimensions()

    @property
    def s(self):
        """This property can be used to get the array size of the cleaner.

        :return: Size of the array of vectors.
        :rtype: int
        """
        return self.c_sl.s()
    @s.setter
    def s(self, s):
        raise ValueError('cannot set the dimensions. it is automatically calculated')
