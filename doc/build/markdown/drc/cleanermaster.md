# kppc.drc.cleanermaster module

Wrapper Class for CleanerMaster.cpp

This Class creates a managed shared memory space. Polygon data for cleaning are streamed into this memory space. A slave process (cleanermain, which is a little loop for CleanerSlave.cpp).

## Python Class


#### class PyCleanerMaster()

#### add_edge(self, x1 : int, x2 : int, y1 : int, y2 : int)
Add an edge to the cleaner.


* **Parameters**

    * **x1** – first x coordinate

    * **x2** – second x coordinate

    * **y1** – first y coordinate

    * **y2** – second y coordinate



#### done(self)
Indicates whether there is data still in the buffer from the last read or not.


* **Returns**

    false if the buffer is empty and the data has been read by the slave.



* **Return type**

    [bool](https://docs.python.org/3/library/functions.html#bool)



#### get_layer(self)
Read the next processed layer in the memory space and returns it in per line style (x coordinates per line (y coordinate)). This is considerably slower than returning the polygons.


#### polygons(self)
Reads the next processed layer in the memory and assembles the line style to polygons.


#### set_box(self, layer : int, datatype : int, violation_width : int, violation_space : int, x1 : int, x2 : int, y1 : int, y2 : int)
Allocate enough space in the shared memory to stream the cell and its polygons in.


* **Parameters**

    * **layer** – layer number

    * **datatype** – datatype number

    * **viospace** (*minimum space violation in database units*) – minimum space violation in database units

    * **viowidth** (*minimum width violation in database units*) – minimum width violation in database units

    * **x1** – left bound of box

    * **x2** – right bound of box

    * **y1** – bottom bound of box

    * **y2** – top bound of box


## C++ Class


#### )

#### )

#### )
Creates the shared memory space and resizes the vectors for nlayers


#### )
Allocate enough space in the shared memory to stream the cell and its polygons in.


#### )
Add an edge to the cleaner.


#### )
Indicates whether there is data still in the buffer from the last read or not.


#### )
Read the next processed layer in the memory space and returns it in per line style (x coordinates per line (y coordinate)).


#### )
Reads the next processed layer in the memory and assembles the line style to polygons.

C++ Source Code: CleanerMaster Source
