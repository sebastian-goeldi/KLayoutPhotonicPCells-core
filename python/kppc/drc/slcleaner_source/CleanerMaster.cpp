#include "CleanerMaster.h"


namespace drclean{

    CleanerMaster::CleanerMaster()
    {
        bi::shared_memory_object::remove("DRCleanEngine");

        bi::named_mutex::remove("mux_inp");
        bi::named_mutex::remove("mux_out");

        segment = new bi::managed_shared_memory(bi::create_only, "DRCleanEngine", 1073741824);

        alloc_inst = new ShmemAllocatorInt(segment->get_segment_manager());

        input = segment->construct<ShIVector>("input") (*alloc_inst);
        outList = segment->construct<ShIVector>("outList") (*alloc_inst);

        mux_inp = new bi::named_mutex(bi::open_or_create, "mux_inp");
        mux_out = new bi::named_mutex(bi::open_or_create, "mux_out");

    }

    CleanerMaster::CleanerMaster(int nlayers)
    {
        CleanerMaster();
        outList->resize(nlayers);
    }

    CleanerMaster::~CleanerMaster()
    {
        bi::shared_memory_object::remove("DRCleanEngine");
        delete segment;
        delete alloc_inst;
        delete mux_out;
        delete mux_inp;
    }

    int CleanerMaster::set_box(int layer, int datatype, int violation_width, int violation_space, int x1, int x2, int y1, int y2)
    {
        local_input.clear();
        local_input.push_back(layer);
        local_input.push_back(datatype);
        local_input.push_back(x1);
        local_input.push_back(x2);
        local_input.push_back(y1);
        local_input.push_back(y2);
        local_input.push_back(violation_space);
        local_input.push_back(violation_width);
        return 0;

    }

    void CleanerMaster::add_edge(int x1, int x2, int y1, int y2)
    {
        local_input.push_back(x1);
        local_input.push_back(x2);
        local_input.push_back(y1);
        local_input.push_back(y2);
    }

    int CleanerMaster::done()
    {
        mux_inp->lock();
        if(!input->empty())
        {
            mux_inp->unlock();
            return 1;
        }

        for(auto iter = local_input.begin();iter!=local_input.end();iter++)
        {
            input->push_back(*iter);
        }

        mux_inp->unlock();

        return 0;
    }

    std::vector<std::vector<int>> CleanerMaster::get_layer()
    {
        std::vector<std::vector<int>> lines;
        mux_out->lock();
        int layer;
        int datatype;
        if(!outList->empty())
        {
            datatype = outList->back();
            outList->pop_back();
            layer = outList->back();
            outList->pop_back();
            mux_out->unlock();
        }
        else
        {
            mux_out->unlock();
            std::vector<int> ld(2,-1);
            lines.push_back(ld);
            return lines;
        }
        std::vector<int> ld{layer,datatype};
        lines.push_back(ld);
        std::string layername = std::to_string(layer) + "/" + std::to_string(datatype);
        ShIVVector* linesVect = segment->find<ShIVVector>(layername.data()).first;

        for(ShIVVector::iterator iter = linesVect->begin(); iter != linesVect->end(); iter++)
        {
            std::vector<int> poly;
            for(ShIVector::iterator iterint = iter->begin(); iterint != iter->end(); iterint++)
            {
                poly.push_back(*iterint);
            }
            lines.push_back(std::move(poly));

        }
        return lines;
    }

    std::vector<std::vector<pi>> CleanerMaster::get_polygons()
    {
        std::vector<std::vector<pi>> polys;

        mux_out->lock();
        int layer;
        int datatype;
        if(!outList->empty())
        {
            datatype = outList->back();
            outList->pop_back();
            layer = outList->back();
            outList->pop_back();
            mux_out->unlock();
        }
        else
        {
            mux_out->unlock();
            std::vector<pi> ld;
            ld.push_back(std::make_pair(-1,-1));
            polys.push_back(ld);
            return polys;
        }
        std::vector<pi> ld;
        ld.push_back(std::make_pair(layer,datatype));
        polys.push_back(ld);
        std::string layername = std::to_string(layer) + "/" + std::to_string(datatype);
        ShPVVector* polygons = segment->find<ShPVVector>(layername.data()).first;

        for(ShPVVector::iterator iter = polygons->begin(); iter != polygons->end(); iter++)
        {
            std::vector<pi> poly;
            for(ShPVector::iterator piter = iter->begin(); piter != iter->end(); piter++)
            {
                poly.push_back(*piter);
            }
            polys.push_back(std::move(poly));
        }
        mux_out->unlock();
        return polys;

    }

}