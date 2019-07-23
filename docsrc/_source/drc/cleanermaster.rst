.. _cm:

kppc.drc.cleanermaster module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Wrapper Class for CleanerMaster.cpp

This Class creates a managed shared memory space. Polygon data for cleaning are streamed into this memory space. A slave process (cleanermain, which is a little loop for CleanerSlave.cpp).

Python Class
""""""""""""

.. class:: PyCleanerMaster

    .. method:: add_edge(self, x1 : int, x2 : int, y1 : int, y2 : int)
        
        Add an edge to the cleaner.
        
        :param x1: first x coordinate
        :type x1: :integers:
        :param x2: second x coordinate
        :type x2: :integers:
        :param y1: first y coordinate
        :type y1: :integers:
        :param y2: second y coordinate
        :type y2: :integers:
        
    .. method:: done(self)
        
        Indicates whether there is data still in the buffer from the last read or not.
        
        :return: false if the buffer is empty and the data has been read by the slave.
        :rtype: bool
    
    .. method:: get_layer(self)
    
        Read the next processed layer in the memory space and returns it in per line style (x coordinates per line (y coordinate)). This is considerably slower than returning the polygons.
        
    .. method:: polygons(self)
    
        Reads the next processed layer in the memory and assembles the line style to polygons.
    
    .. method:: set_box(self, layer : int, datatype : int, violation_width : int, violation_space : int, x1 : int, x2 : int, y1 : int, y2 : int)
        
        Allocate enough space in the shared memory to stream the cell and its polygons in.
        
        :param layer: layer number
        :param datatype: datatype number
        :type layer: :integers:
        :param viospace: minimum space violation in database units
        :type viospace: minimum space violation in database units
        :param viowidth: minimum width violation in database units
        :type viowidth: minimum width violation in database units
        :param x1: left bound of box
        :type x1: :integers:
        :param x2: right bound of box
        :type x2: :integers:
        :param y1: bottom bound of box
        :type y1: :integers:
        :param y2: top bound of box
        :type y2: :integers:

C++ Class
"""""""""


.. cpp:class:: CleanerMaster

        .. cpp:function:: CleanerMaster(int nlayers)
            
            Creates the shared memory space and resizes the vectors for nlayers
            
        .. cpp:function:: void set_box(int layer, int datatype, int violation_width, int violation_space, int x1, int x2, int y1, int y2)
            
            Allocate enough space in the shared memory to stream the cell and its polygons in.
            
        .. cpp:function:: void add_edge(int x1, int x2, int y1, int y2)
            
            Add an edge to the cleaner.
            
        .. cpp:function:: bool done()
        
            Indicates whether there is data still in the buffer from the last read or not.
            
        .. cpp:function:: std::vector<std::vector<int>> get_layer()
        
            Read the next processed layer in the memory space and returns it in per line style (x coordinates per line (y coordinate)).
        
        .. cpp:function:: std::vector<std::vector<std::pair<int,int>>> get_polygons()
        
            Reads the next processed layer in the memory and assembles the line style to polygons.
            

        
C++ Source Code: :ref:`cmsource`
