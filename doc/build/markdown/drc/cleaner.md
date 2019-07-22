# kppc.drc.slcleaner module

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
