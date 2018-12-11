.. _slcleaner:

kppc.drc.slcleaner module
^^^^^^^^^^^^^^^^^^^^^^^^^


An interface to the DrcSl.cpp Class.

.. class:: kppc.drc.slcleaner.PyDrcSl


    .. method:: def add_data(x1, x2, y1, y2)

        Insert data into the scanline cleaner. The data is an edge that will be manhattanized and cleaned.

        .. note:: Edges should be added in such a way that the 
            outwards face is left in the direction of p1 to p2.
            Klayout already does this nicely.

        :param x1: x position of p1 of the edge
        :type x1: int
        :param x2: y position of p1 of the edge
        :type x2: int
        :param y1: x position of p2 of the edge
        :type y1: int
        :param y2: y position of p2 of the edge
        :type y2: int

    .. method:: init_list(x1: int, x2: int, y1: int, y2: int, viospace: int, viowidth: int)
        
        (Re-)Initialize the Cleaner. x1,2 and y1,2 define the bounding box of the cleaner.

        .. warning ::

            If a corner or a complete edge is outside the bounding box and is added through the add_data function, a Segmentation Fault will most likely occur and the module (including Klayout) crashes. Alternatively, it will just be confined to the bounding box and the rest will be cut off.

        :param x1: left bound of box
        :type x1: 
        :param x2: right bound of box
        :type x2: 
        :param y1: bottom bound of box
        :type y1: bottom bound of box
        :param y2: top bound of box
        :type y2: top bound of box
        :param viospace: minimum space violation in database units
        :type viospace: minimum space violation in database units
        :param viowidth: minimum width violation in database units
        :type viowidth: minimum width violation in database units
        
    .. method:: sort()
        
        Sort the data in ascending order. This will also delete invalid edges, i.e. touching / overlapping polygons will be merged.
        
    .. method:: clean(x = 10)
        
        Clean data in the vector for space and width violations.

        :param x: number of max tries
    
    .. method:: printvector(beg = -1, end = -1)
    
        Print the data of rows/columns depending on current orientation

        :param beg: beginning of the rows/columns that should be printed
        :type beg:  :integers:
        :param end: ending of the rows/columns that should be printed
        :type end:  :integers:
    
    .. method:: get_row(ind: int)
    
        Get the edge data back to python from the C++ object.

        :param ind: index of the row to retrieve data from
        :type ind: :integers:
        :return: numpy array of the edges
    
    .. method:: get_row_types(ind: int)
    
        Get the type of edges in that row.

        :param ind: index of the row
        :type ind: :integers:
        :return: numpy array of types of edges (0 for upwards facing edge, 1 for downwards)
    
    .. method:: clean_space()
    
        Clean the current data for space violations.
    
    .. method:: clean_width()
    
        Clean the current data for width violations.
    
    .. method:: switch_dimensions()
    
        Switch the orientation of the data. From row oriented to column oriented and vice-versa.
    
    .. method:: s()
    
        This property can be used to get the array size of the cleaner.

        :return: Size of the array of vectors.
        :rtype: int
    
This wrapper is used to expose the design rule cleaner class to the python PCells of KLayout.
The algorithm is pasted below. The algorithm uses a `Scanline Rendering Algorithm <https://en.wikipedia.org/wiki/Scanline_rendering>`_
to first convert the polygons from KLayout to manhattanized edges and then add them into an array representation
of the polygon edges.


C++ Code:

.. literalinclude:: ../../python/kppc/drc/slcleaner_source/DrcSl.cpp
    :language: c++
