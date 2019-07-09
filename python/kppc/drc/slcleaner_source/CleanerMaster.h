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

typedef std::pair<int,int> pi;

typedef bi::allocator<int, bi::managed_shared_memory::segment_manager>  ShmemAllocatorInt;
typedef bi::vector<int, ShmemAllocatorInt> ShIVector;
typedef bi::allocator<ShIVector, bi::managed_shared_memory::segment_manager> ShmemAllocatorIVec;
typedef bi::vector<ShIVector, ShmemAllocatorIVec> ShIVVector;
typedef bi::allocator<pi, bi::managed_shared_memory::segment_manager> ShmemAllocatorPair;
typedef bi::vector<pi,ShmemAllocatorPair> ShPVector;
typedef bi::allocator<ShPVector, bi::managed_shared_memory::segment_manager> ShmemAllocatorPVec;
typedef bi::vector<ShPVector, ShmemAllocatorPVec> ShPVVector;

namespace drclean{

    class CleanerMaster
    {

        public:
            CleanerMaster();
            CleanerMaster(int nlayers);
            virtual ~CleanerMaster();

            int set_box(int layer, int datatype, int violation_width, int violation_space, int x1, int x2, int y1, int y2);
            void add_edge(int x1, int x2, int y1, int y2);
            int done();

            std::vector<std::vector<int>> get_layer();
            bi::managed_shared_memory* segment;
            std::vector<std::vector<pi>> get_polygons();

        private:

            std::vector<int> local_input;
            ShmemAllocatorInt* alloc_inst;
            ShIVector *input;
            ShIVector *outList;
            bi::named_mutex* mux_inp;
            bi::named_mutex* mux_out;
            ShPVVector *polygons;

    };
}

#endif // CC_H