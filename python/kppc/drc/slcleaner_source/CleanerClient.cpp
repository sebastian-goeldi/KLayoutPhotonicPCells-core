#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/containers/vector.hpp>
#include <boost/interprocess/allocators/allocator.hpp>
#include <boost/interprocess/sync/named_mutex.hpp>
#include <boost/interprocess/sync/named_semaphore.hpp>
#include <string>
#include <cstdlib> //std::system

#include <iostream>

#include "CleanerClient.h"

namespace bi = boost::interprocess;
typedef bi::allocator<int, bi::managed_shared_memory::segment_manager>  ShmemAllocatorInt;


namespace drclean{

    CleanerClient::CleanerClient()
//        : segment(bi::open_or_create, "DRCleanEngine", 524288), alloc_inst(segment->get_segment_manager())
    {
        bi::shared_memory_object::remove("DRCleanEngine");


        bi::named_mutex::remove("mux_inp");
        bi::named_mutex::remove("mux_out");

        segment = new bi::managed_shared_memory(bi::create_only, "DRCleanEngine", 1073741824);

        alloc_inst = new ShmemAllocatorInt(segment->get_segment_manager());

        input = segment->construct<ShIVector>("input") (*alloc_inst);

//        input_done = segment->construct<bool>("input_done")(0);

        mux_inp = new bi::named_mutex(bi::open_or_create, "mux_inp");
        mux_inp = new bi::named_mutex(bi::open_or_create, "mux_out");

    }

    CleanerClient::~CleanerClient()
    {
        bi::shared_memory_object::remove("DRCleanEngine");
        delete segment;
        delete alloc_inst;
        delete mux_out;
        delete mux_inp;
    }

    int CleanerClient::set_box(int layer, int datatype, int violation_width, int violation_space, int x1, int x2, int y1, int y2)
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

//        std::cout << "Initializing: " << layer << " " << datatype << " " << x1 << " " << x2 << " " << y1  << " " << y2 << " " << violation_space  << " " << violation_width << std::endl;
//
//        auto iter = input->begin();
//        for (int i = 0; i < 8; i ++)
//        {
//            std::cout << *iter << " ";
//            iter++;
//        }
//        std::cout << std::endl;

        return 0;

    }

    void CleanerClient::add_edge(int x1, int x2, int y1, int y2)
    {
        local_input.push_back(x1);
        local_input.push_back(x2);
        local_input.push_back(y1);
        local_input.push_back(y2);
    }

    int CleanerClient::done()
    {
//        *input_done = 1;

//        ShIVector::iterator it = input->begin();
//
//        if(!(*input_done))
//        {
//            for(it = input->begin();it != input->end(); it++)
//            {
//                std::cout << "it: " << *it << std::endl;
//            }
//        }
//        std::cout << "unlocking :D" << std::endl;

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
//        std::cout << "unlocked" << std::endl;

//        std::cout << "Done" << std::endl;
    }

}

//using namespace drclean;

//int main(int argc, char* argv[])
//{
////    bi::shared_memory_object::remove("DRCleanEngine");
//    struct shm_remove {
//		shm_remove() { bi::shared_memory_object::remove("DRCleanEngine"); }
//	    ~shm_remove() { bi::shared_memory_object::remove("DRCleanEngine"); }
//	} remover;
//    std::cout << "Creating Object" << std::endl;
//    CleanerClient client;
//    std::cout << "Setting Boundaries" << std::endl;
//    std::cout << client.set_box(0,0,0,500,0,500) << std::endl;
//    std::cout << "Adding Edge" << std::endl;
//    client.add_edge(50,100,50,50);
//    std::cout << "Printing Vector" << std::endl;
//    client.done();
//
////    bi::shared_memory_object::remove("DRCleanEngine");
//
//}










//using namespace boost::interprocess;

//Define an STL compatible allocator of ints that allocates from the managed_shared_memory.
//This allocator will allow placing containers in the segment
//typedef allocator<int, managed_shared_memory::segment_manager>  ShmemAllocatorInt;
//
//typedef allocator<drclean::edgecord, managed_shared_memory::segment_manager>  ShmemAllocatorE;
//
//
//Alias a vector that uses the previous STL-like allocator so that allocates
//its values from the segment
//typedef vector<int, ShmemAllocator> ShVector;
//
//typedef vector<drclean::edgecord, ShmemAllocatorEdgeCoord> ShEVector;

//Main function. For parent process argc == 1, for child process argc == 2
//int main(int argc, char *argv[])
//{
////   if(argc == 1){ //Parent process
////      //Remove shared memory on construction and destruction
////      struct shm_remove
////      {
////         shm_remove() { shared_memory_object::remove("MySharedMemory"); }
////         ~shm_remove(){ shared_memory_object::remove("MySharedMemory"); }
////      } remover;
////
////      //Create a new segment with given name and size
////      managed_shared_memory segment(create_only, "MySharedMemory", 65536);
////
////      //Initialize shared memory STL-compatible allocator
////      const ShmemAllocator alloc_inst (segment.get_segment_manager());
////
////      //Construct a vector named "ShVector" in shared memory with argument alloc_inst
////      ShVector *shvector = segment.construct<ShVector>("ShVector")(alloc_inst);
////
////      for(int i = 0; i < 100; ++i)  //Insert data in the vector
////         shvector->push_back(i);
////
////      //Launch child process
////      std::string s(argv[0]); s += " child ";
////      if(0 != std::system(s.c_str()))
////         return 1;
////
////      //Check child has destroyed the vector
////      if(segment.find<ShVector>("ShVector").first)
////         return 1;
////   }
////   else{ //Child process
//      //Open the managed segment
//      managed_shared_memory segment(open_or_create, "DRCleanEngine", 524288);
//
//      //Find the vector using the c-string name
//      ShVector *shvector = segment.find<ShVector>("ShVector").first;
//
//      //Use vector in reverse order
//      //std::sort(shvector->rbegin(), shvector->rend());
//      vector<int, ShmemAllocator>::iterator it;
//
//      for (it = shvector->begin();it != shvector->end(); it++)
//      {
//        std::cout << "it: " << *it << std::endl;
//      }
//
//      //When done, destroy the vector from the segment
//      segment.destroy<ShVector>("ShVector");
////   }
//
//   return 0;
//};


////Define an STL compatible allocator of ints that allocates from the managed_shared_memory.
////This allocator will allow placing containers in the segment
//typedef bi::allocator<int, bi::managed_shared_memory::segment_manager>  ShmemAllocatorInt;
//
//typedef bi::allocator<drclean::edgecoord, bi::managed_shared_memory::segment_manager>  ShmemAllocatorE;
//
////Alias a vector that uses the previous STL-like allocator so that allocates
////its values from the segment
//typedef bi::vector<int, ShmemAllocatorInt> ShIVector;
//
//typedef bi::vector<drclean::edgecoord, ShmemAllocatorE> ShEVector;
