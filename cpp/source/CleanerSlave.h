//  This file is part of KLayoutPhotonicPCells, an extension for Photonic Layouts in KLayout.
//  Copyright (c) 2018, Sebastian Goeldi
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU Affero General Public License as
//    published by the Free Software Foundation, either version 3 of the
//    License, or (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU Affero General Public License for more details.
//
//    You should have received a copy of the GNU Affero General Public License
//    along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

#include <utility>

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

typedef std::pair<int,int> pi;

typedef bi::allocator<int, bi::managed_shared_memory::segment_manager>  ShmemAllocatorInt;
typedef bi::vector<int, ShmemAllocatorInt> ShIVector;

typedef bi::allocator<ShIVector, bi::managed_shared_memory::segment_manager> ShmemAllocatorIVec;
typedef bi::vector<ShIVector, ShmemAllocatorIVec> ShIVVector;

typedef bi::allocator<pi, bi::managed_shared_memory::segment_manager> ShmemAllocatorPair;
typedef bi::vector<pi,ShmemAllocatorPair> ShPVector;
typedef bi::allocator<ShPVector, bi::managed_shared_memory::segment_manager> ShmemAllocatorPVec;
typedef bi::vector<ShPVector, ShmemAllocatorPVec> ShPVVector;

namespace drclean
{

class CleanerSlave
{

public:
    CleanerSlave();
    virtual ~CleanerSlave();
    bool initialized = false;
    void clean();
    void join_threads();

private:
    bi::managed_shared_memory* segment;

    ShmemAllocatorInt* alloc_inst;
    ShmemAllocatorIVec* alloc_vec;
    ShmemAllocatorPVec* alloc_pvec;
    ShmemAllocatorPair* alloc_poly;

    ShIVector* input;
    ShIVector* outList;

    ShPVVector* polygons;

    bi::named_mutex* mux_inp;
    bi::named_mutex* mux_out;

    void threaded_DrcSl(std::vector<int> *inp);

    boost::asio::thread_pool * pool;

};

}

#endif //CE_H
