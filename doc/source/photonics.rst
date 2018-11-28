photonics package
=================

This package is a library extension for KLayout to provide functionalities for photonic structures.

.. warning:: KLayout does not check if a loaded module has changed during runtime and thus does not reread/recompile it.
    This means you either must manually reload the library if you want to do it during runtime. Generally, it is easier and
    safer to close and reopen KLayout.
    
    If this extension is modified (or any file in a ``/python`` directory), don't forget to either reload the module or
    reopen KLayout.
    
    .. note:: To reload a module during runtime use the following commands in the KLayout python console (not guaranteed to work in all cases):
        
        >>> from importlib import reload
        >>> import <module>
        >>> reload(<module>)

Module contents
---------------

.. automodule:: photonics
    :members:
    :undoc-members:
    :show-inheritance:

Submodules
----------

photonics.dataprep module
^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: photonics.dataprep
    :members:
    :undoc-members:
    :show-inheritance:

photonics.layermaps module
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: photonics.layermaps
    :members:
    :undoc-members:
    :show-inheritance:
