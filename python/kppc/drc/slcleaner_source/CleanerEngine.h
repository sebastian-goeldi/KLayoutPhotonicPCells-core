#ifndef CE_H
#define CE_H

#include <boost/array.hpp>

#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/containers/vector.hpp>
#include <boost/interprocess/allocators/allocator.hpp>
#include <boost/interprocess/sync/named_mutex.hpp>

#include <boost/asio/thread_pool.hpp>
#include <boost/asio.hpp>

#include <boost/thread.hpp>

#include <signal.h>

#include <string>
#include <cstdlib> //std::system

#include <iostream>

#include "DrcSl.h"
#include "SignalHandler.h"

#include <vector>

#include <thread>
#include <chrono>

namespace bi = boost::interprocess;

typedef bi::allocator<int, bi::managed_shared_memory::segment_manager>  ShmemAllocatorInt;
typedef bi::vector<int, ShmemAllocatorInt> ShIVector;

typedef bi::allocator<ShIVector, bi::managed_shared_memory::segment_manager> ShmemAllocatorIVec;
typedef bi::vector<ShIVector, ShmemAllocatorIVec> ShIVVector;

namespace drclean{

    class CleanerEngine
    {

    public:
        CleanerEngine();
        virtual ~CleanerEngine();
        bool initialized = false;
        void clean();
        void join_threads();

    private:
        bi::managed_shared_memory* segment;

        ShmemAllocatorInt* alloc_inst;
        ShmemAllocatorIVec* alloc_vec;

        ShIVector* input;
        ShIVector* outList;

        bi::named_mutex* mux_inp;
        bi::named_mutex* mux_out;

        void threaded_DrcSl(std::vector<int> *inp);

        boost::asio::thread_pool * pool;

    };

}

#endif //CE_H