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
from libcpp.vector cimport vector
from libcpp cimport bool


cdef extern from "DrcSl.cpp":
    pass

cdef extern from "DrcSl.h" namespace "drclean":
    cdef cppclass DrcSl:
        DrcSl() except +

        void initialize_list(int, int, int, int, int, int)
        void add_data(int x1, int x2, int y1, int y2)
        void sortlist()
        void clean(int max_tries)

        bool list_cleaning()
        int clean_space()
        int clean_width()
        void switch_dimensions()
        void printvector(int beg, int ende)

        vector[int] get_vect(int ind)
        vector[int] get_types(int ind)
        vector[vector[int]] get_lines()
        int violation_width
        int violation_space
        int hor1
        int hor2
        int ver1
        int ver2
        int s()
