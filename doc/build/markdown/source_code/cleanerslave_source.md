# CleanerSlave Source

```
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

#include "CleanerSlave.h"


namespace drclean
{
CleanerSlave::CleanerSlave()
{
    segment = new bi::managed_shared_memory(bi::open_only, "DRCleanEngine");

    std::cout<< "Initializing" << std::endl;

    alloc_inst = new ShmemAllocatorInt(segment->get_segment_manager());
    alloc_vec = new ShmemAllocatorIVec(segment->get_segment_manager());
    alloc_pvec = new ShmemAllocatorPVec(segment->get_segment_manager());
    alloc_poly = new ShmemAllocatorPair(segment->get_segment_manager());

    input = segment->find<ShIVector>("input").first;
    outList = segment->find<ShIVector>("outList").first;
//        imList = segment->find<ShIVector>("imList").first;

    mux_inp = new bi::named_mutex(bi::open_only, "mux_inp");
    mux_out = new bi::named_mutex(bi::open_only, "mux_out");

    pool = new boost::asio::thread_pool(boost::thread::hardware_concurrency());

    if (input)
    {
        initialized = true;
    }
}

CleanerSlave::~CleanerSlave()
{
    join_threads();
    delete alloc_inst;
    delete pool;
}

void CleanerSlave::clean()
{
    std::vector<int> *inp = new std::vector<int>();
    mux_inp->lock();
    if(!input->empty())
    {
        bi::vector<int, ShmemAllocatorInt>::iterator it;
        for(it = input->begin(); it != input->end(); it++)
        {
            inp->push_back(*it);
        }
        input->clear();
        mux_inp->unlock();
    }
    else
    {
        mux_inp->unlock();
        delete inp;

        std::this_thread::sleep_for(std::chrono::milliseconds(30));
        return;
    }

    boost::asio::post(*pool,boost::bind(&CleanerSlave::threaded_DrcSl,this,inp));
//        threaded_DrcSl(inp); //For single thread calculation
}

void CleanerSlave::threaded_DrcSl(std::vector<int> *inp)
{
    int layer;
    int datatype;

    DrcSl sl;
    std::vector<int>::iterator iter = inp->begin();

    if(iter!=inp->end())
    {
        layer = *(iter++);
        datatype = *(iter++);
        sl.initialize_list(*(iter),*(iter+1),*(iter+2),*(iter+3),*(iter+4),*(iter+5));
        // The first six datapoints are size (x1,x2,y1,y2) and layer, datatype information.
        int count = 6;
        iter+=6;
        while(iter!=inp->end())
        {
            count +=4;
            sl.add_data(*(iter),*(iter+1),*(iter+2),*(iter+3));
            iter+=4;
        }
    }
    else
    {
        delete inp;
        return;
    }

    delete inp;
    sl.sortlist();
    sl.clean();
    std::string layername = std::to_string(layer) + "/" + std::to_string(datatype);

    std::vector<std::vector<pi>> polys = sl.get_polygons();

    ShPVVector* polygons = segment->construct<ShPVVector>(layername.data())(*alloc_pvec);

    for(auto p: polys)
    {
        ShPVector* poly = segment->construct<ShPVector>(bi::anonymous_instance) (*alloc_poly);
        for(auto pit: p)
        {
            poly->push_back(pit);
        }
        polygons->push_back(boost::move(*poly));
    }
    mux_out->lock();
    outList->push_back(layer);
    outList->push_back(datatype);
    mux_out->unlock();

}

void CleanerSlave::join_threads()
{
    pool->join();
}

};
```
