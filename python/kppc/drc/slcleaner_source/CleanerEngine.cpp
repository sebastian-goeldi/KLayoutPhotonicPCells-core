#include "CleanerEngine.h"


namespace drclean{
    CleanerEngine::CleanerEngine()
    {
        segment = new bi::managed_shared_memory(bi::open_only, "DRCleanEngine");

        alloc_inst = new ShmemAllocatorInt(segment->get_segment_manager());
        alloc_vec = new ShmemAllocatorIVec(segment->get_segment_manager());

        input = segment->find<ShIVector>("input").first;
        outList = segment->find<ShIVector>("outList").first;

        mux_inp = new bi::named_mutex(bi::open_only, "mux_inp");
        mux_out = new bi::named_mutex(bi::open_only, "mux_out");

        pool = new boost::asio::thread_pool(boost::thread::hardware_concurrency());

        if (input)
        {
            initialized = true;
        }
    }

    CleanerEngine::~CleanerEngine()
    {
        join_threads();
        delete alloc_inst;
        delete pool;
    }

    void CleanerEngine::clean()
    {

        std::vector<int> *inp = new std::vector<int>();
        mux_inp->lock();
        if(!input->empty())
        {

            bi::vector<int, ShmemAllocatorInt>::iterator it;
            for(it = input->begin();it != input->end(); it++)
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

        boost::asio::post(*pool,boost::bind(&CleanerEngine::threaded_DrcSl,this,inp));
    }

    void CleanerEngine::threaded_DrcSl(std::vector<int> *inp)
    {
        int layer;
        int datatype;

        DrcSl sl;
        std::vector<int>::iterator iter = inp->begin();

        if(iter!=inp->end())
        {
            int count = 6;
            layer = *(iter++);
            datatype = *(iter++);
            sl.initialize_list(*(iter),*(iter+1),*(iter+2),*(iter+3),*(iter+4),*(iter+5));
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
            std::cout << "*hurgh*" << std::endl;
            delete inp;
            return;
        }

        delete inp;
        sl.sortlist();
        sl.clean();
        std::vector<std::vector<int>> lines = sl.get_lines();
        std::string layername = std::to_string(layer) + "/" + std::to_string(datatype);

        ShIVVector* linevec = segment->construct<ShIVVector>(layername.data())(*alloc_vec);
        for(std::vector<std::vector<int>>::iterator iter =  lines.begin(); iter!=lines.end();iter++)
        {
            ShIVector* line = segment->construct<ShIVector>(bi::anonymous_instance) (*alloc_inst);
            for(std::vector<int>::iterator iterint=iter->begin(); iterint!=iter->end(); iterint++)
            {
                line->push_back(*iterint);
            }
            linevec->push_back(boost::move(*line));
        }

        mux_out->lock();
        outList->push_back(layer);
        outList->push_back(datatype);
        mux_out->unlock();

    }

    void CleanerEngine::join_threads()
    {
        pool->join();
    }

};

int main(int argc, char* argv[])
{
    drclean::CleanerEngine ce = drclean::CleanerEngine();

    if (!ce.initialized)
    {
        return -1;
    }

    SignalHandler signalHandler;
    signalHandler.setSignalToHandle(SIGUSR1);

    while(!signalHandler.isSignalSet())
    {
        ce.clean();
    }
}