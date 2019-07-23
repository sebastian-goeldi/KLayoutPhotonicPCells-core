# drc Module

## Module contents

This module uses the C++ submodule slcleaner. It has to be compiled after installing the
extension.

To compile the module execute the setup script `scripts/compile.sh`.
Or alternatively execute the `python/kppc/drc/slcleaner_source/setup.py` with the python3 executable
and copy/move the resulting `slcleaner.[...].so` library file ino the `python/drc/` folder.

For further information consult the [Cython Documentation](http://cython.org/).

To execute the script open a console and execute the following commands:

```
cd ~/.klayout/salt/KLayoutPhotonicPCells/core/scripts
sh compile.sh
```

The bash script executes the following commands:

```
#!/bin/bash

#Script that compiles the C++ scanline algorithm with cython to a python module and copies it into the current folder
#If there is an __init__.py in the folder the setup script will create subfolders, so avoid that

sh ./clean
sh ./compile.sh
```


#### kppc.drc.clean(cell, cleanrules)
Clean a cell for width and space violations.
This function will clear the output layers of any shapes and insert a cleaned region.


* **Parameters**

    * **cell** (*pya.Cell*) – pointer to the cell that needs to be cleaned

    * **cleanrules** ([`list`](https://docs.python.org/3/library/stdtypes.html#list)) – list with the layerpurposepairs, violationwidths and violationspaces in the form [[[layer,
      purpose], violationwidth, violationspace], [[layer2, purpose2], violationwidth2, violationspace2], …]



#### kppc.drc.multiprocessing_clean(cell, cleanrules)
Clean a cell for width and space violations.
This function will clear the output layers of any shapes and insert a cleaned region.
Does the cleaning in a seperate Process started as a childprocess,
which will calculate in parallel with multiple threads.


* **Parameters**

    * **cell** (*pya.Cell*) – pointer to the cell that needs to be cleaned

    * **cleanrules** ([`list`](https://docs.python.org/3/library/stdtypes.html#list)) – list with the layerpurposepairs, violationwidths and violationspaces in the form [[[layer,
      purpose], violationwidth, violationspace], [[layer2, purpose2], violationwidth2, violationspace2], …]


## Submodules

### kppc.drc.slcleaner module

An interface to the DrcSl.cpp Class.


#### class kppc.drc.slcleaner.PyDrcSl()

#### def add_data(x1, x2, y1, y2)()
Insert data into the scanline cleaner. The data is an edge that will be manhattanized and cleaned.

**NOTE**: Edges should be added in such a way that the
outwards face is left in the direction of p1 to p2.
Klayout already does this nicely.


* **Parameters**

    * **x1** ([*int*](https://docs.python.org/3/library/functions.html#int)) – x position of p1 of the edge

    * **x2** ([*int*](https://docs.python.org/3/library/functions.html#int)) – y position of p1 of the edge

    * **y1** ([*int*](https://docs.python.org/3/library/functions.html#int)) – x position of p2 of the edge

    * **y2** ([*int*](https://docs.python.org/3/library/functions.html#int)) – y position of p2 of the edge



#### clean(x = 10)
Clean data in the vector for space and width violations.


* **Parameters**

    **x** – number of max tries



#### clean_space()
Clean the current data for space violations.


#### clean_width()
Clean the current data for width violations.


#### init_list(x1: int, x2: int, y1: int, y2: int, viospace: int, viowidth: int)
(Re-)Initialize the Cleaner. x1,2 and y1,2 define the bounding box of the cleaner.

**WARNING**: If a corner or a complete edge is outside the bounding box and is added through the add_data function, a Segmentation Fault will most likely occur and the module (including Klayout) crashes. Alternatively, it will just be confined to the bounding box and the rest will be cut off.


* **Parameters**

    * **x1** – left bound of box

    * **x2** – right bound of box

    * **y1** – bottom bound of box

    * **y2** (*:integers*) – top bound of box

    * **viospace** (*minimum space violation in database units*) – minimum space violation in database units

    * **viowidth** (*minimum width violation in database units*) – minimum width violation in database units



#### get_row(ind: int)
Get the edge data back to python from the C++ object.


* **Parameters**

    **ind** – index of the row to retrieve data from



* **Returns**

    numpy array of the edges



#### get_row_types(ind: int)
Get the type of edges in that row.


* **Parameters**

    **ind** – index of the row



* **Returns**

    numpy array of types of edges (0 for upwards facing edge, 1 for downwards)



#### polygons()
Returns list of crude polygons. The format is list of polygons, where a polygon is a list of tuples of (x,y)


* **Returns**

    polygons in the form [[(x1,y1),(x2,y2),…],…]



* **Return_type**

    list



#### printvector(beg = -1, end = -1)
Print the data of rows/columns depending on current orientation


* **Parameters**

    * **beg** – beginning of the rows/columns that should be printed

    * **end** – ending of the rows/columns that should be printed



#### s()
This property can be used to get the array size of the cleaner.


* **Returns**

    Size of the array of vectors.



* **Return type**

    [int](https://docs.python.org/3/library/functions.html#int)



#### sort()
Sort the data in ascending order. This will also delete invalid edges, i.e. touching / overlapping polygons will be merged.


#### switch_dimensions()
Switch the orientation of the data. From row oriented to column oriented and vice-versa.

This wrapper is used to expose the design rule cleaner class to the python PCells of KLayout.
The algorithm is pasted below. The algorithm uses a [Scanline Rendering Algorithm](https://en.wikipedia.org/wiki/Scanline_rendering)
to first convert the polygons from KLayout to manhattanized edges and then add them into an array representation
of the polygon edges.

Source Code: DrcSl Source

## Multiprocessing

With version 0.1.0 multiprocessing was introduced. Multiprocessing allows to use all threads of the machine to process the DRC cleaning on all threads of the CPU in parallel. This can give a considerable speed boost if multiple layers are involved and the hardware supports it.

### kppc.drc.cleanermaster module

Wrapper Class for CleanerMaster.cpp

This Class creates a managed shared memory space. Polygon data for cleaning are streamed into this memory space. A slave process (cleanermain, which is a little loop for CleanerSlave.cpp).

#### Python Class


#### class kppc.drc.PyCleanerMaster()

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


#### C++ Class


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

### CleanerMain

C++ documentation of the cleanermain. This program is a simple program with a loop that processes any layers added to the shared memory. If the process receives SIGUSER1, it joins the threads and terminates afterwards.

Source: CleanerMain Source

### CleanerSlave

C++ documentation of the Class CleanerSlave


#### )

#### )
Constructor of the Class
The constructor opens the shared memory and initializes the allocators for the shared memory. Initializes a boost thread_pool with as many threads as the CPU supports (one per core).


#### )
Checks if the shared memory has a cell layer added. If there is a layer to process, move the data to shared memory and schedule it for processing by the thread_pool.


#### )
Wait for the thread_pool to finish all jobs and return

Source Code: CleanerSlave Source
