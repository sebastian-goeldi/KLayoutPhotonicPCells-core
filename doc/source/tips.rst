Tips & Tricks
=============

Variable Names in KLayout Python
--------------------------------

When using global variables in pymacros (scripts like cell libraries) be careful. Namespace is shared between macros. This means when for example defining the names of metal layers in two cells, one can overwrite the other one.
Therefore the use of global variables is not advised and the use of a wrapper class is recommended instead. It can be defined in the same wrapper class used for defining layernames and cleaning information, for example.
