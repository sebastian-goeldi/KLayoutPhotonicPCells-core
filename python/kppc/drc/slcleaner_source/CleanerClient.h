#ifndef CC_H
#define CC_H

#include <vector>
#include "DrcSl.h"
#include <boost/array.hpp>
#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/containers/vector.hpp>
#include <boost/interprocess/allocators/allocator.hpp>
#include <boost/interprocess/sync/named_mutex.hpp>
#include <string>
#include <cstdlib> //std::system
#include <utility>
#include <iostream>


namespace bi = boost::interprocess;

typedef bi::allocator<int, bi::managed_shared_memory::segment_manager>  ShmemAllocatorInt;
typedef bi::vector<int, ShmemAllocatorInt> ShIVector;
typedef bi::allocator<ShIVector, bi::managed_shared_memory::segment_manager> ShmemAllocatorIVec;
typedef bi::vector<ShIVector, ShmemAllocatorIVec> ShIVVector;

namespace drclean{

    class CleanerClient
    {

        public:
            CleanerClient();
            CleanerClient(int nlayers);
            virtual ~CleanerClient();

            int set_box(int layer, int datatype, int violation_width, int violation_space, int x1, int x2, int y1, int y2);
            void add_edge(int x1, int x2, int y1, int y2);
            int done();

            std::vector<std::vector<int>> get_layer();
            bi::managed_shared_memory* segment;

        private:

            std::vector<int> local_input;
            ShmemAllocatorInt* alloc_inst;
            ShIVector *input;
            ShIVector *outList;
            bi::named_mutex* mux_inp;
            bi::named_mutex* mux_out;

    };
}

#endif // CC_H