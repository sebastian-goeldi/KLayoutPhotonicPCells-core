#ifndef CE_H
#define CE_H

#include <vector>

namespace bi = boost::interprocess;

//Define an STL compatible allocator of ints that allocates from the managed_shared_memory.
//This allocator will allow placing containers in the segment
typedef bi::allocator<int, bi::managed_shared_memory::segment_manager>  ShmemAllocatorInt;

typedef bi::allocator<drclean::edgecoord, bi::managed_shared_memory::segment_manager>  ShmemAllocatorE;

//Alias a vector that uses the previous STL-like allocator so that allocates
//its values from the segment
typedef bi::vector<int, ShmemAllocatorInt> ShIVector;

typedef bi::vector<drclean::edgecoord, ShmemAllocatorE> ShEVector;

namespace drclean{

    class CleanerEngine
    {

    public:
        CleanerEngine();
        virtual ~CleanerEngine();

        void clean();


    protected:
        bi::managed_shared_memory * segment;

        ShmemAllocatorInt* alloc_inst;
        ShIVector * input;
        bool * input_done;

    };

}

#endif //CE_H