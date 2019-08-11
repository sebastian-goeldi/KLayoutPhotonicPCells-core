Introduction
============

The KLayoutPhotonicPCells`kppc` module is an extension for KLayout PCells to facilitate photonic PCells.
Photonics often works with the concept of ports.
Ports are defined by a coordinate and a direction. In the case of this module ports will be stored in PCell parameters in the background.
They are serialized `KLayout Trans`_ objects. For an introduction on how to build your own PCell Library, have a look at
how to create :doc:`Example Library <photonics/example_library>`.

When building PCell Libraries it is recommended to build it with three packages as shown in :numref:`p_format`

.. figure:: _static/pictures/package_format.svg
    :name: p_format
    :width: 100 %
    :alt: The intended use for this library extension is to work with 3 packages per PCell-Library. First this one, second a technology specific
        package which contains techfile and import from techfile and finally the PCell Library.
    
    The recommend structure for working with the photonic PCell extension:
    * Photonic Library Extension: New functionalities for KLayout PCells
        
        * Ports, DR-Cleaning, DataPrep
    
    * Technology: Contains manufacturer specific data
    
        * Design rules
        * Layermapping from abstract to manufacturer layers
        
    * PCell-Library:
    
        * Definitions of PCells
        * Library specific modules if required        


.. _KLayout Trans: https://www.klayout.de/doc/code/class_ICplxTrans.html
