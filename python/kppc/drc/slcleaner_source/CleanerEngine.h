#ifndef CE_H
#define CE_H


namespace bi = boost::interprocess;

//Define an STL compatible allocator of ints that allocates from the managed_shared_memory.
//This allocator will allow placing containers in the segment
typedef bi::allocator<int, bi::managed_shared_memory::segment_manager>  ShmemAllocatorInt;

typedef bi::allocator<int[2], bi::managed_shared_memory::segment_manager>  ShmemAllocatorInt2;

typedef bi::allocator<drclean::edgecoord, bi::managed_shared_memory::segment_manager>  ShmemAllocatorE;

//Alias a vector that uses the previous STL-like allocator so that allocates
//its values from the segment
typedef bi::vector<int, ShmemAllocatorInt> ShIVector;
typedef bi::vector<int[2], ShmemAllocatorInt> ShIIVector;
typedef bi::vector<drclean::edgecoord, ShmemAllocatorE> ShEVector;

namespace drclean{

    class CleanerEngine
    {

    public:
        CleanerEngine();
        virtual ~CleanerEngine();
        bool initialized = false;
        void clean();
        void join_threads();

    protected:

        bi::managed_shared_memory * segment;

        ShmemAllocatorInt* alloc_inst;
        ShIVector * input;

        ShIVector * done_threads;

        bi::named_mutex* mux_inp;
        bi::named_mutex* mux_out;

        void threaded_DrcSl(std::vector<int> *inp);
//        boost::thread_group * tg;
        boost::asio::thread_pool * pool;

    };

}

#endif //CE_H