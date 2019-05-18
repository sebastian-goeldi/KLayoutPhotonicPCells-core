#ifndef CC_H
#define CC_H

#include <vector>
#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/containers/vector.hpp>
#include <boost/interprocess/allocators/allocator.hpp>
#include "DrcSl.h"


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

    class CleanerClient
    {

        public:
            CleanerClient();
            virtual ~CleanerClient();

            int set_box(int layer, int datatype, int violation_width, int violation_space, int x1, int x2, int y1, int y2);
            void add_edge(int x1, int x2, int y1, int y2);
            void done();
            bi::managed_shared_memory* segment;

        private:

            ShmemAllocatorInt* alloc_inst;
            ShIVector *input;
            bool * input_done;

    };

//    class CleanerEngine
//    {
//    };

}

#endif // CC_H