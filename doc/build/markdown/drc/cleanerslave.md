# CleanerSlave

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
