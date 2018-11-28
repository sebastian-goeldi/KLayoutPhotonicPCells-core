First Steps
===========

Prerequisites
-------------

To use the library extension, make sure you have installed Cython. Part of the cleaning process relies on a C++ module that needs to be compiled first. To compile it we use pythons :doc:`Setuptools <setuptools:index>` and :doc:`Cython <cython:index>`. Make sure you have these packages before starting. It is sufficient to install Cython, as setuptools is either built-in of python or installed along Cython.

Installation
------------

This installation procedure is solely written for Linux. For this installation Cython is required. So get Cython either from the package manager of your distribution or through pip. The package is tested on Python 3.5+. No special python3 modules are used, therefore it should work with python 2.7, too. The Python version used should be the same KLayout uses. By default, this is the system interpreter for Python3.
If you installed the package manually, move the unpackaged package into ``~/.klayout/salt`` or into the KLayout folder if you used a custom directory. This tutorial assumes default pathes.
After unpacking and moving you should have a ``~/.klayout/salt/zccmos/pcell_ext_lib`` folder. If you installed the FreePDK45_Cells & FreePDK45_tech, then you should have the folders ``~/.klayout/salt/zccmos/FreePDK45_Cells`` and ``~/.klayout/salt/zccmos/FreePDK45_tech``, too. The library extension package needs manual setup before being usable.

Use a console and execute the following commands. If you are familiar with setuptools you can skip these instructions. For further information consult the :py:mod:`drc` documentation.

.. code-block:: console
    
    cd ~/.klayout/salt/zccmos/pcell_ext_lib/python/drc/
    ./setup

.. figure:: _static/pictures/Cython.png
    :width: 100 %
    :alt: Compile the C++Python module with Cython
    
    Change directory to the drc folder and execute the setup script.
 
