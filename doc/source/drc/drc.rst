drc Module
===========

Module contents
---------------

.. automodule:: kppc.drc
    :members:
    :undoc-members:
    :show-inheritance:

Submodules
----------

.. include:: cleaner.rst


Multiprocessing
---------------

With version 0.1.0 multiprocessing was introduced. Multiprocessing allows to use all threads of the machine to process the DRC cleaning on all threads of the CPU in parallel. This can give a considerable speed boost if multiple layers are involved and the hardware supports it.

.. include:: cleanermaster.rst
.. include:: cleanermain.rst
.. include:: cleanerslave.rst
