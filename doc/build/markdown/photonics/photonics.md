# photonics Module

This package is a library extension for KLayout to provide functionalities for photonic structures.

**WARNING**: KLayout does not check if a loaded module has changed during runtime and thus does not reread/recompile it.
This means you either must manually reload the library if you want to do it during runtime. Generally, it is easier and
safer to close and reopen KLayout.

If this extension is modified (or any file in a `/python` directory), don’t forget to either reload the module or
reopen KLayout.

**NOTE**: To reload a module during runtime use the following commands in the KLayout python console (not guaranteed to work in all cases):

```python
>>> from importlib import reload
>>> import <module>
>>> reload(<module>)
```

## Module contents

Photonic PCell-Extension Module

**WARNING**: Before using this module for the first time, make sure the kppc.drc.slcleaner submodule is compiled and importable, as this  module
relies on the drc package for DR-Cleaning. See `drc` for further details.

A Module which provides extensions for standard KLyaout-PCells. This extension mainly provides functionalities for
photonics. One main feature of photonics are so-called ports. These define a position and a direction on a Cell.
They indicate where multiple Cells/Devices should interact with each other. For example, one can connect a waveguide
with a linear taper. This module provides the classes and functions for this functionality. Additionally, this module
provides a lot of convenience functions for interactions with the KLayout-API.

The main functionality for this module is in the class `PhotDevice`.

**WARNING**: When using this module to extend a PCell-Library any PCell class has to assign valid values to the
parameters `layermap` , `dataprep_config` , `clean_rules` . These are accessed by `PhotDevice`. If they
aren’t declared, a runtime error will occur.


#### class kppc.photonics.InstanceHolder(cell_name, lib, pcell_decl, params=None, params_mod=None, id=0)
Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Class to keep track and hold the information of a pcell instance. The information will be processed to a PCell in
`produce_impl()`


#### move(x=0, y=0, rot=0, mirrx=False, mag=1)
Moves an instance. Units of microns relative to origin.


* **Parameters**

    * **x** ([*float*](https://docs.python.org/3/library/functions.html#float)) – x position where to move

    * **y** ([*float*](https://docs.python.org/3/library/functions.html#float)) – y position where to move

    * **rot** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Rotation of the object in degrees

    * **mirrx** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Mirror at x-axis if True

    * **mag** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Magnification of the Cell. This feature is not tested well.



#### port(port)
Returns a reference to itself and the port number. No checks are made whether this port is valid or not!
Available ports can be seen if such an object is instantiated.


* **Parameters**

    **port** ([`int`](https://docs.python.org/3/library/functions.html#int)) – index of the port



* **Returns**

    self, port



#### port_to_port(port, inst_holder)
Attach one of this instance’s ports to another instance’s port.


* **Parameters**

    * **port** ([`int`](https://docs.python.org/3/library/functions.html#int)) – port of this instance

    * **inst_holder** ([`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple)) – Tuple of the the reference to the other instance and the port to connect to.
      This is a tuple returned from <InstanceHolder object>.port(<portnumber>).



#### class kppc.photonics.PhotDevice()
Bases: `pya.PCellDeclarationHelper`

Wrapper for calls to the Klayout API.


* **Variables**

    * **layermap** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – The layermap dictionary. This value has to be written by a child class. If undefined this
      class won’t work and crash.

    * **dataprep_config** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – String with the path to the file containing the dataprep instructions.
      If left empty, dataprep will do nothing.

    * **clean_rules** ([*list*](https://docs.python.org/3/library/stdtypes.html#list)) – String with the path to the file containing the DR-Cleaning rules.
      If left empty, DR-Cleaning will do nothing. If the cells are built similar to the FreePDK45-SampleCells example,
      DR-Cleaning will not work without dataprep, or will be without any effect.

    * **keep** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Parameter created during `__init__()` via pya.DeclarationHelper. If set to True in the PCell,
      all child-cells will be preserved at the end. If set to False only the Dataprep Sub-Cell will be preserved.

    * **dataprep** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If this flag is set, `kppc.photonics.dataprep.dataprep()` will be performed on the cell. The variable
      `dataprep_config` holds the path to the instructions for dataprep.

    * **clean** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If this flag is set, `kppc.drc.clean()` will be performed on the cell. Rules for the DR-Cleaning
      are pulled from `clean_rules`.

    * **top** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Hidden parameter that indicates whether this cell is a top_cell. Default is yes. When an instance is
      added through `add_pcell_variant()` these cells will not be set to top_cells as they are instantiated from
      another cell.

    * **only_top_ports** – GUI parameter. If set to true, only ports of the top most hierarchy level (top_cell) will be
      annotated by text.



#### add_layer(var_name, name='', layer=0, datatype=0, ld=(), field_name='', hidden=False)
Add a layer to the layer list of the pcell by name.


* **Parameters**

    * **var_name** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – name of the variable

    * **name** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – name in the pcell window

    * **layer** ([`int`](https://docs.python.org/3/library/functions.html#int)) – layernumber

    * **datatype** ([`int`](https://docs.python.org/3/library/functions.html#int)) – layerdatatype

    * **field_name** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – 

    * **hidden** – hide in the GUI



* **Examples**

    self.add_layer(‘lpp’,’rx1phot.drawing’)



#### add_params(params)
Create the PCell conform dictionary from a parameter list


* **Parameters**

    **params** ([`dict`](https://docs.python.org/3/library/stdtypes.html#dict)) – Dictionary of parameters



#### add_pcell_variant(params, number=1)
Add variants of PCells. Creates a list of InstanceHolders and modifies their parameters accordingly.


* **Parameters**

    * **params** ([`dict`](https://docs.python.org/3/library/stdtypes.html#dict)) – parameter list from which to create pcells

    * **number** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Number of instances to create



* **Returns**

    list of `kppc.photonics.InstanceHolder`



#### add_pcells(instance_list)
Creates list of instances of PCells. These are the effective Klayout cell instances.


* **Parameters**

    **instance_list** ([`list`](https://docs.python.org/3/library/stdtypes.html#list)) – list of `kppc.photonics.InstanceHolder`



* **Returns**

    list of instantiated pya.CellInstArray



#### calculate_ports(instances)
Calculates port locations in the cell layout. This is to propagate the port locations upwards


* **Parameters**

    **instances** ([`list`](https://docs.python.org/3/library/stdtypes.html#list)) – list containing `kppc.photonics.InstanceHolder`



#### clear_ports()
Clears self.portlist and by that delete all ports. This is used when updating the Ports


#### coerce_parameters_impl()
Method called by Klayout to update a PCell. For photonic PCells the ports are updated/calculated in the
parameter of the PCell. And desired movement transformations are performed.

Because the calculated ports of our own PCell are used by parent cells and are needed before
~produce_impl, we must calculate them twice. First to calculate where our own ports are and then again to
instantiate the child cells. This is unfortunate but not a big problem, since dataprep and DR-cleaning take
the majority of computation time.


* **Returns**

    


#### connect_port(pos1, portlist1, port1, pos2, portlist2, port2)
Connect ports of two instances. The second instance will be transformed to attach to the first instance.


* **Parameters**

    * **pos1** ([`int`](https://docs.python.org/3/library/functions.html#int)) – index of instance1

    * **portlist1** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – portlist of instance1

    * **port1** ([`int`](https://docs.python.org/3/library/functions.html#int)) – port number of instance1

    * **pos2** ([`int`](https://docs.python.org/3/library/functions.html#int)) – index of instance2

    * **portlist2** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – portlist of instance2

    * **port2** ([`int`](https://docs.python.org/3/library/functions.html#int)) – port number of instance2



* **Return type**

    `None`



#### connect_port_to_port(port1, port2)
Connect Ports from two InstanceHolder instances.

Connect two InstanceHolders together. Attach <InstanceHolder instance1>.port(<port1>) to <InstanceHolder instance2>.port(<port2>).
This will apply a transformation to Instance2. There can only be either a transformation through connect_port_to_port or through InstanceHolder.move


* **Parameters**

    * **port1** ([`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple)) – <InstanceHolder instance1>.port(<port1>)

    * **port2** ([`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple)) – <InstanceHolder instance2>.port(<port2>)



#### create_param_inst()
To be overwritten by the effective PCell


* **Returns**

    Iterable with the declarations of the child PCells.



#### create_path(points, width, layer)
Creates a pya.Path object and inserts it into the Library-PCell.


* **Parameters**

    * **points** ([`list`](https://docs.python.org/3/library/stdtypes.html#list)) – The points describing the path [[x1,y1],[x2,y2],…] in microns

    * **width** ([`float`](https://docs.python.org/3/library/functions.html#float)) – Path width

    * **layer** (*pya.LayerInfo*) – layer on which the path should be made



#### create_polygon(points, layer)
Creates a Polygon and adjusts from microns to database units. Format: [[x1,y1],[x2,y2],…] in microns


* **Parameters**

    * **points** ([`list`](https://docs.python.org/3/library/stdtypes.html#list)) – Points defining the corners of the polygon.

    * **layer** ([`int`](https://docs.python.org/3/library/functions.html#int)) – layer_index of the target layer



* **Returns**

    reference to polygon object



#### create_port(x, y, rot=0, length=0)
Creates a Port at the specified coordinates.

This function will be used when a port is created through the PortCreation tuple.


* **Parameters**

    * **x** ([`float`](https://docs.python.org/3/library/functions.html#float)) – x Coordinate in microns

    * **y** ([`float`](https://docs.python.org/3/library/functions.html#float)) – y Coordinate in microns

    * **rot** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Rotation in degrees

    * **length** ([`int`](https://docs.python.org/3/library/functions.html#int)) – length of the port in microns



#### decl(libname, cellname)
Get pya.PCellDeclaration of a cell in a library


* **Parameters**

    * **libname** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the library

    * **cellname** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the cell



* **Returns**

    pya.PCellDeclaration reference of PCell



#### flip_shape_xaxis(shape)
Flip a polygon (or any shape) at the x-axis


* **Parameters**

    **shape** (*pya.Shape*) – pya.Shape object (e.g. through photonicpcell.create_polygon obtained)



#### flip_shape_yaxis(shape)
Flip a polygon (or any shape) at the y-axis


* **Parameters**

    **shape** (*pya.Shape*) – pya.Shape object (e.g. through photonicpcell.create_polygon obtained)



#### get_layer(name, purpose='')
Creates LayerInfo object

Creates a pya.LayerInfo object to find layer indexes in the current layout.


* **Parameters**

    * **name** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – name of the layer

    * **purpose** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – if not empty then layer and purpose are separate



* **Returns**

    pya.LayerInfo about the layer



#### get_transformations()
Convert transformation strings back to pya.ICplxTrans objects


* **Returns**

    list of pya.ICplxTrans objects



#### insert_shape(shape, layer)
Any other Klayout shape can be added to the PCell through this function.


* **Parameters**

    * **shape** (*pya.Shape*) – pya.Shape object

    * **layer** (*pya.LayerInfo*) – layer where to write to



* **Returns**

    reference to shape



#### move_instance(ind, trans, mirror=False)
Moves an InstanceHolder object


* **Parameters**

    * **ind** ([`int`](https://docs.python.org/3/library/functions.html#int)) – id of the InstanceHolder

    * **trans** (*pya.ICplxTrans*) – list of transformations

    * **mirror** ([`bool`](https://docs.python.org/3/library/functions.html#bool)) – bool whether to mirror the object



#### produce_impl()
Create the effective Klayout shapes. For this all the InstanceHolders are cycled through and all the child
instances are created. Furthermore, if desired, dataprep is performed, which copies and sizes the shapes as
desired. Dataprep will only create shapes on the topmost cell. Finally, if desired DR-cleaning is performed and
in the process the shapes will be manhattanized.


#### set_transformation(ind, trans)
Transforms child cells to the intended position, defined either by connected ports or by manual
positioning.


* **Parameters**

    * **ind** ([`int`](https://docs.python.org/3/library/functions.html#int)) – index of the child cell

    * **trans** (*pya.ICplxTrans*) – Transformation object with which to transform the child cell



#### shapes()
To be overwritten by effective PCell if shapes should be desired.


* **Return type**

    [None](https://docs.python.org/3/library/constants.html#None)



#### update_parameter_list(params, decl)
Coerces parameter list. This is necessary to calculate port locations and update parameters in general.


* **Parameters**

    * **params** ([`dict`](https://docs.python.org/3/library/stdtypes.html#dict)) – dict of parameters

    * **decl** (*pya.PCellDeclaration*) – pya.PCellDeclaration reference



* **Returns**

    list of updated parameters



#### class kppc.photonics.PortCreation(x, y, rot, length)
Bases: [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple)

Custom namedtuple

This will hold informations for creating ports.


* **Parameters**

    * **x** ([*int*](https://docs.python.org/3/library/functions.html#int)) – x Coordinate [microns]

    * **y** ([*int*](https://docs.python.org/3/library/functions.html#int)) – y Coordinate [microns]

    * **rot** – Rotation in degrees

    * **length** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Port length [microns]



#### property length()
Alias for field number 3


#### property rot()
Alias for field number 2


#### property x()
Alias for field number 0


#### property y()
Alias for field number 1


#### kppc.photonics.isnamedtupleinstance(x)
Test if something is a named tuple
This allows to test if x is a port (PortCreation object) or just a list of instance descriptions

## Submodules

### photonics.dataprep module


#### kppc.photonics.dataprep.add(layout, cell, slayers, dlayers, ex_amount, layers, out_cell=None)
Combines all slayers’ shapes into a region and merges this region with each of dlayers’ regions.


* **Parameters**

    * **layout** – the layout on which the cells are located

    * **cell** – the cell from which to copy the layers (source shapes)

    * **slayers** – the layers to copy

    * **dlayers** – the layers where to copy to

    * **ex_amount** – the amount added around the source shapes

    * **layers** – the layermapping

    * **out_cell** – the cell where to put the shapes. If not specified, the input cell will be used.



#### kppc.photonics.dataprep.dataprep(in_cell, layout, out_cell=None, config=None, layers_org=None)
Dataprep that creates excludes layers etc. with boolean operation on input layers that will be added/substracted to outputlayers.


* **Parameters**

    * **in_cell** – the cell from which to take shapes

    * **layout** – the layout on which we perform the operations (most likely self.layout)

    * **out_cell** – the output cell. if not specified take the input cell

    * **config** – the config file. This file specifies the boolean operations (self.dataprepconfig)

    * **layers_org** – the original layermap we use (most likely self.layermap)



#### kppc.photonics.dataprep.file_len(fname)
Returns the number of lines in the file fname


#### kppc.photonics.dataprep.sub(layout, cell, slayers, dlayers, ex_amount, layers, out_cell=None)
Analogous to `add()`

Instead of perfoming a combination with the destination layers, this function will substract the input region.

### photonics.layermaps module


#### kppc.photonics.layermaps.load(filename)
Simple routine to read a .layermap file into a dictionary


* **Parameters**

    **filename** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Filename with path



* **Returns**

    Dictionary of dictionaries in the form of {layer: {purpose1:(layer_number,purpose_number),
    purpose2:(layer_number1,purpose_number2)},layer2: {…} }



* **Return type**

    [dict](https://docs.python.org/3/library/stdtypes.html#dict)



* **Examples**

    ```python
    >>> import kppc.photonics.layermaps as lm
    >>> lm.load(os.path.expanduser('~/.klayout/salt/zccmos/FreePDK45_tech/tech/FreePDK45.layermap'))
    {'pwell': {'blockage': ('109', '1'), 'drawing': ('109', '0')}, ... }
    ```
