.. _cs:

CleanerSlave
^^^^^^^^^^^^

C++ documentation of the Class CleanerSlave

.. cpp:class:: CleanerSlave
    

    .. cpp:member:: void CleanerSlave()
            
        Constructor of the Class
        The constructor opens the shared memory and initializes the allocators for the shared memory. Initializes a boost thread_pool with as many threads as the CPU supports (one per core).

            
    .. cpp:member:: void clean()
        
        Checks if the shared memory has a cell layer added. If there is a layer to process, move the data to shared memory and schedule it for processing by the thread_pool.
        

    .. cpp:member:: void join_threads()
        
        Wait for the thread_pool to finish all jobs and return

Source Code: :ref:`cssource`
