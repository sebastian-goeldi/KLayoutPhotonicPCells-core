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
#include "CleanerEngine.h"
#include "SignalHandler.h"

#include <vector>

#include <thread>
#include <chrono>

//testing
#include <fstream>


namespace drclean{
    CleanerEngine::CleanerEngine()
    {
        segment = new bi::managed_shared_memory(bi::open_only, "DRCleanEngine");

        alloc_inst = new ShmemAllocatorInt(segment->get_segment_manager());

//        input_done = segment->find<bool>("input_done").first;

        input = segment->find<ShIVector>("input").first;

        mux_inp = new bi::named_mutex(bi::open_only, "mux_inp");
        mux_out = new bi::named_mutex(bi::open_only, "mux_out");

        pool = new boost::asio::thread_pool(boost::thread::hardware_concurrency());

//        tg = new boost::thread_group();
        if (input)
        {
            initialized = true;
        }
    }
    CleanerEngine::~CleanerEngine()
    {
//        delete segment;
        join_threads();
        delete alloc_inst;
//        delete tg;
    }

    void CleanerEngine::clean()
    {

        std::vector<int> *inp = new std::vector<int>();
//        std::cout << "Locking input" << std::endl;
        mux_inp->lock();
//        std::cout << "Locked" << std::endl;
        if(!input->empty())
        {

            std::cout << input->size() << std::endl;
            bi::vector<int, ShmemAllocatorInt>::iterator it;
            for(it = input->begin();it != input->end(); it++)
            {
                inp->push_back(*it);
            }
            input->clear();
//            std::cout << "cleared input :P" << std::endl;
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






//        boost::thread * th = new boost::thread(&CleanerEngine::threaded_DrcSl,this,inp);
//        tg->add_thread(th);

//        th->join();

//        threaded_DrcSl();


    }

    void CleanerEngine::threaded_DrcSl(std::vector<int> *inp)
    {
//        std::cout << "Unlocked" << std::endl;

        /*std::ofstream myFile;
        myFile.open("test.txt", std::ios::app);
        myFile << "New Layer" << std::endl;
        std::vector<int>::iterator iter;
        for(iter=inp->begin();iter!=inp->end();iter++)
        {
            myFile << *iter;
        }
        myFile << std::endl;
        myFile.close();
        return;*/
        int layer;
        int datatype;

        DrcSl sl;
        std::vector<int>::iterator iter = inp->begin();

//        std::cout << "Initialized Cleaner, size: " << inp->size() << ", size/4: " << (double)inp->size() / 4 << std::endl;

        if(iter!=inp->end())
        {
            int count = 6;
//            std::cout << (*inp)[0] << " " << (*inp)[1] << " " << (*inp)[2] << " " << (*inp)[3] << " " << (*inp)[4] << " " << (*inp)[5] << " " << std::endl;
            layer = *(iter++);
            datatype = *(iter++);

//            std::cout << "layer: " << layer << " datatype: " << datatype << std::endl;

//            std::cout << "iters: " << *iter << " " << *(iter+1) << " " << *(iter+2) << " " << *(iter+3) << " " << *(iter+4) << " " << *(iter+5) << std::endl;

            sl.initialize_list(*(iter),*(iter+1),*(iter+2),*(iter+3),*(iter+4),*(iter+5));
//            std::cout << "Initialized list" << std::endl;
            iter+=6;
            while(iter!=inp->end())
            {
                count +=4;
                sl.add_data(*(iter),*(iter+1),*(iter+2),*(iter+3));
                iter+=4;
//                std::cout << count << '/' << inp->size() << std::endl;
            }
        }
        else
        {
            std::cout << "*hurgh*" << std::endl;
            delete inp;
            return;
        }

        delete inp;

//        std::cout << "Filled data" << std::endl;

        sl.sortlist();
        sl.clean();
        std::vector<std::vector<int>> polygons = sl.polygons();
        std::cout << "We have " << polygons.size() << " number of polygons on layer " << layer << "/" << datatype << std::endl;
//        mux_out->lock();
//        std::cout << "Theoretically cleaned vector" << std::endl;
//        mux_out->unlock();
//        std::this_thread::sleep_for(std::chrono::milliseconds(10));

    }

    void CleanerEngine::join_threads()
    {
//        tg->join_all();
        pool->join();
    }

};

int main(int argc, char* argv[])
{
    drclean::CleanerEngine ce = drclean::CleanerEngine();

    if (!ce.initialized)
    {
        std::cout << "Initialization failed, aborting!" << std::endl;
        return -1;
    }

    SignalHandler signalHandler;
    signalHandler.setSignalToHandle(SIGUSR1);

    while(!signalHandler.isSignalSet())
    {
        ce.clean();
    }
}




/*using namespace boost::interprocess;

//Define an STL compatible allocator of ints that allocates from the managed_shared_memory.
//This allocator will allow placing containers in the segment
typedef allocator<int, managed_shared_memory::segment_manager>  ShmemAllocator;

//Alias a vector that uses the previous STL-like allocator so that allocates
//its values from the segment
typedef vector<int, ShmemAllocator> ShVector;

//Main function. For parent process argc == 1, for child process argc == 2
int main(int argc, char *argv[])
{
//   if(argc == 1){ //Parent process
      //Remove shared memory on construction and destruction
      struct shm_remove
      {
         shm_remove() { shared_memory_object::remove("MySharedMemory"); }
         ~shm_remove(){ shared_memory_object::remove("MySharedMemory"); }
      } remover;

      //Create a new segment with given name and size
      managed_shared_memory segment(create_only, "MySharedMemory", 65536);

      //Initialize shared memory STL-compatible allocator
      const ShmemAllocator alloc_inst (segment.get_segment_manager());

      //Construct a vector named "ShVector" in shared memory with argument alloc_inst
      ShVector *shvector = segment.construct<ShVector>("ShVector")(alloc_inst);

      for(int i = 0; i < 100; ++i)  //Insert data in the vector
         shvector->push_back(i);

      //Launch child process
//      std::string s(argv[0]); s += " child ";
//      if(0 != std::system(s.c_str()))
//         return 1;


      std::this_thread::sleep_for(std::chrono::milliseconds(20000));

      //Check child has destroyed the vector
      if(segment.find<ShVector>("ShVector").first)
         return 1;
//   }

   return 0;
};*/



//#include "DrcSl.h"
//#include <iostream>
//#include <fstream>
//#include <string>
//#include <sstream>
//#include <stdexcept>
//#include <cmath>

//#include <boost/interprocess/managed_shared_memory.hpp>
//#include <boost/interprocess/containers/vector.hpp>
//#include <boost/interprocess/allocators/allocator.hpp>

//namespace drclean{
//
////    Function to compare two edgecoord structs. This is necessary for std::sort. If they are on the same coordinate sort for type in descending order
//    bool compare_edgecoord(edgecoord e1, edgecoord e2)
//    {
//        if (e1.pos==e2.pos)
//            return (e2.type<e1.type);
//        else
//            return (e1.pos<e2.pos);
//    }
//
////    Constructor. Initialize the pointers as nullptrs
//    DrcSl::DrcSl()
//    {
//        this->lver = nullptr;
//        this->lhor = nullptr;
//    }
//
////    Destructor: Delete the allocated vectors.
//    DrcSl::~DrcSl()
//    {
//        if(this->lhor != nullptr)
//            delete[] this->lhor;
//        if(this->lver != nullptr)
//            delete[] this->lver;
//    }
//
////    Add a complete data-set. Currently not used and not exposed in the Python interface.
//    int DrcSl::set_data(std::vector<edgecoord> *horlist)
//    {
//        this->l = horlist;
//        return 0;
//    }
//
////    Initialize the dimensions of the vector arrays and set pointers accordingly and dimension units.
//    void DrcSl::initialize_list(int hor1,int hor2, int ver1, int ver2, int violation_space, int violation_width)
//    {
//        if(this->lhor)
//        {
//            delete[] this->lhor;
//            this->lhor = nullptr;
//        }
//        if(this->lver)
//        {
//            delete[] this->lver;
//            this->lver = nullptr;
//        }
//        this->lhor = new std::vector<edgecoord>[ver2-ver1+5];
//        this->lver = new std::vector<edgecoord>[hor2-hor1+5];
//        this->l = this->lhor;
//        this->sver = hor2-hor1+5;
//        this->shor = ver2-ver1+5;
//        this->hor1 = hor1-2;
//        this->hor2 = hor2+2;
//        this->ver1 = ver1-2;
//        this->ver2 = ver2+2;
//        this->violation_space = violation_space;
//        this->violation_width = violation_width;
//        this->orientation = hor;
//    }
//
////    Print the complete data set or from index beg -> end if they are set.
////    -1, -1 will result in printing the whole vector.
//    void DrcSl::printvector(int beg, int last)
//    {
//        if (last == -1 && beg == -1)
//        {
//            last = this->orientation ? this->ver2 : this->hor2;
//            beg = this->orientation ? this->ver1 : this->hor1;
//        }
//        std::vector<edgecoord>::iterator it;
//
//        std::cout << "size, y: " << this->sver << std::endl << "size, x: " << this->shor << std::endl;
//        int offset = this->orientation ? -this-> hor1 : -this-> ver1;
//        int offset_d2 = this->orientation ? -this->ver1 : -this-> hor1;
//        std::cout << "beg/end " << beg+offset << '/' << last+offset-1 << std::endl;
//
//        for (int i = 0; i < this->s(); i++)
//        {
//            std::cout << "row: " << i-offset << ": [";
//            for(it = this->l[i].begin(); it != this->l[i].end(); it++)
//            {
//                std::cout << "(" << it->pos -offset_d2<< "," << it->type << ")";
//            }
//            std::cout << "]" << std::endl;
//        }
//    }
//
////    Get the current array size of the vectors
//    int DrcSl::s()
//    {
//        return this->orientation ? this->sver : this->shor;
//    }
//
//
////  Sort all data with compare_edge_coord and remove overlapping edges, i.e. merge overlapping polygons in the data
//    void DrcSl::sortlist()
//    {
//        std::cout << this->s() << std::endl;
//        for (int i = 0; i < this->s(); i++)
//        {
//            if (!this->l[i].empty())
//            {
//                std::sort(this->l[i].begin(),this->l[i].end(),compare_edgecoord);
//                std::vector<edgecoord>::iterator it;
//                it = this->l[i].begin();
//                int c = 0;
//                for(;it != this->l[i].end();it++)
//                {
//                    if (it->type == 0)
//                    {
//                        c++;
//                        if (c>1 || c<0)
//                        {
//                            it->rem = true;
//                        }
//                    }
//                    else
//                    {
//                        if (c>1 || c<0)
//                        {
//                            it->rem = true;
//                        }
//                        c--;
//                    }
//                }
//                this->l[i].erase(std::remove_if(this->l[i].begin(),this->l[i].end(),[](auto o) { return o.rem; }),this->l[i].end());
//
//            }
//        }
//    }
//
////    Get data from a row (or column).
////    If used after the standard sorting or cleaning function, i.e. sortlist() and cleaning(),
////    the vectors should always be arranged row-oriented, meaning the same format as when added to the cleaner.
//    std::vector<int> DrcSl::get_vect(int ind)
//    {
//        int offset = this->orientation ? -this->hor1 : -this-> ver1;
//        int offset_d2 = this->orientation ? -this->ver1 : -this-> hor1;
//
//        std::vector<int> res = std::vector<int>(this->l[ind+offset].size());
//        std::vector<edgecoord>::iterator it;
//        int i;
//        for(it = this->l[ind+offset].begin(),i=0; it !=this->l[ind+offset].end(); it++,i++)
//        {
//            if (it->type)
//                res[i]=(it->pos-1-offset_d2);
//            else
//                res[i]=(it->pos+1-offset_d2);
//        }
//
//        return res;
//    }
//
////    Function to print the types in a vector. Probably only useful for debugging purposes
//    std::vector<int> DrcSl::get_types(int ind)
//    {
//        int offset = this->orientation ? -this->hor1 : -this-> ver1;
//
//        offset ++;
//
//        std::vector<int> res = std::vector<int>(this->l[ind+offset].size());
//        std::vector<edgecoord>::iterator it;
//        int i;
//        for(it = this->l[ind+offset].begin(),i=0; it !=this->l[ind+offset].end(); it++,i++)
//        {
//            res[i] = it->type;
//        }
//
//        return res;
//    }
//
////    Add data to the data structure. We manhattanize the edge from the input and mark left facing edges with -1 and
////    right facing edges with +1. The get_vect() function reverses this effect.
////    This should have no influence on any possible data except that it merges touching polygons.
//    void DrcSl::add_data(int px1, int px2, int py1, int py2)
//    {
//        int offset = this->orientation ? -this-> hor1 : -this-> ver1;
//        int offset_d2 = this->orientation ? -this->ver1 : -this-> hor1;
//
//        if (py2 > py1)
//        {
//            edgecoord p  = edgecoord(px1+offset_d2-1,0);
//
//            double dx = (double)(px2-px1)/(py2-py1);
//            double x = p.pos;
//            if (p.pos < 0 || p.pos > (this->orientation ? this->shor : this->sver))
//            {
//                std::cout << "Error ROW (y) index out of bound " << p.pos << '/' << (this->orientation ? this->shor: this->sver) << std::endl;
//                throw 1;
//            }
//            if (offset+py1 < 0 || py2+offset > this->s())
//            {
//                std::cout << "Error COLUMN (x) index out of bound" << std::endl;
//                throw 2;
//            }
//
//            if (dx > 0)
//            {
//                for(int i = offset+py1; i < py2+offset; i++)
//                {
//                    this->l[i].push_back(p);
//                    x+=dx;
//                    p.pos = int(x);
//                }
//            }
//            else
//            {
//                for(int i = offset+py1; i < py2+offset-1; i++)
//                {
//                    x+=dx;
//                    p.pos = int(x);
//                    this->l[i].push_back(p);
//                }
//                p.pos = px2+offset_d2-1;
//                this->l[py2+offset-1].push_back(p);
//            }
//
//        }
//        else if (py1 > py2)
//        {
//            edgecoord p  = edgecoord(px2+offset_d2+1,1);
//
//            double dx = (double)(px1-px2)/(py1-py2);
//            double x = p.pos;
//            if (p.pos < 0 || p.pos > (this->orientation ? this->shor : this->sver))
//            {
//                std::cout << "Error ROW (y) index out of bound " << p.pos << '/' << (this->orientation ? this->shor: this->sver) << std::endl;
//                throw 1;
//            }
//            if (offset+py1 < 0 || py2+offset > this->s())
//            {
//                std::cout << "Error COLUMN (x) index out of bound" << std::endl;
//                throw 2;
//            }
//
//            if (dx < 0)
//            {
//                for(int i = offset+py2; i < py1+offset; i++)
//                {
//                    this->l[i].push_back(p);
//                    x+=dx;
//                    p.pos = std::ceil(x);
//                }
//            }
//            else
//            {
//            for(int i = offset+py2; i < py1+offset-1; i++)
//                {
//                    x+=dx;
//                    p.pos = std::ceil(x);
//                    this->l[i].push_back(p);
//                }
//                p.pos = px1+offset_d2+1;
//                this->l[py1+offset-1].push_back(p);
//            }
//        }
//    }
//
////    Clean data for space violations in the current orientation (row-oriented for violations within the row and accordingly if column-oriented).
//    int DrcSl::clean_space()
//    {
//        //Cleans space violations.
//        //Returns number of space violations that were cleaned.
//        std::vector<edgecoord> *il = this->l;
//
//        //Counters to keep track of how many checks were done and how many space violations have been cleaned.
//        int spacevios = 0;
//        int counts = 0;
//
//        std::vector<edgecoord>::iterator it;
//
//        for (int i = 0; i<this->s();i++)
//        {
//            if (!il->empty())
//            {
//                bool er = false;
//                it = il->begin();
//                if (it == il->end())
//                    continue;
//                it++;
//                while(it+1 != il->end())
//                {
//                    counts++;
//                    if ((it+1)->pos - it->pos < violation_space -1)
//                    {
//                        er = true;
//                        spacevios++;
//                        it->rem = true;
//                        (it+1)->rem = true;
//                    }
//                    it+=2;
//                }
//                if (er)
//                    il->erase(std::remove_if(il->begin(),il->end(),[](auto o) { return o.rem; }),il->end());
//            }
//            il++;
//        }
////        If progress output is desired uncomment the following lines
////        std::cout << "number of checks: " << counts << std::endl;
////        std::cout << "violations, space: " << spacevios << std::endl;
//        return spacevios;
//
//    }
//
////    Clean data for width violation
//    int DrcSl::clean_width()
//    {
//        std::vector<edgecoord> *il = this->l;
//
//        int widthvios = 0;
//        int counts = 0;
//
//        std::vector<edgecoord>::iterator it;
//
//        for (int i = 0; i<this->s();i++)
//        {
//            if (!il->empty())
//            {
//                bool er=false;
//                it = il->begin();
//                while(it != il->end())
//                {
//                    counts++;
//                    if ((it+1)->pos - it->pos < violation_width +1)
//                    {
//                        er = true;
//                        it->rem = true;
//                        (it+1)->rem = true;
//                        widthvios++;
//                    }
//                    it+=2;
//                }
//                if (er)
//                    il->erase(std::remove_if(il->begin(),il->end(),[](auto o) { return o.rem; }),il->end());
//
//            }
//            il++;
//        }
////        If progress output is desired uncomment the following lines
////        std::cout << "number of checks: " << counts << std::endl;
////        std::cout << "violations, width: " << widthvios << std::endl;
//        return widthvios;
//
//    }
//
//
////    Calculate difference between two rows or two columns. This is necessary when switching from row-oriented to
////    column-oriented data and vice-versa.
////
////    In theory this can also be used to check for minimum edge-lengths. But for us all of these requirements have been
////    waived, so we don't have to check for those.
//    std::vector<int> DrcSl::listdif(std::vector<edgecoord> &l1, std::vector<edgecoord> &l2)
//    {
//        /*
//        **  Calculates differences between rows (or columns, depending on orientation) between two vectors (rows/columns)
//        **  The difference between the two vectors indicate that there is a polygon border for the other orientation of the scanlines
//        **  This border corresponds to edges and thus has to appear in the opposite orientation
//        */
//
//        /*
//        **  Example:
//        **
//        **  l1 is the row/column that we compare to. Any coordinates that appear in l1, but not in l2, will be returned as ranges.
//        **  example:
//        **  l1 = ([1,5],[7,10],[18,20])
//        **  l2 = ([4,11],[15,16])
//        **  out = ([1,3],[18,20])
//        */
//
//        std::vector<int> out;
//        std::vector<edgecoord>::iterator it1 = l1.begin();
//        std::vector<edgecoord>::iterator it2 = l2.begin();
//        int l21;
//        int l22;
//        for (it1 = l1.begin(); it1 !=l1.end(); it1++)
//        {
//            int b = it1->pos;
//            it1++;
//            int e = it1->pos;
//            int ee = e;
//            bool add = true;
//            while(it2 != l2.end())
//            {
//                l21 = it2->pos;
//                l22 = (it2+1)->pos;
//                if(l22 < b)
//                {
//                    it2+=2;
//                }
//                else if (l22 >= e)
//                {
//                    if (e < b || l21 <= b)
//                        add = false;
//                    if (e > l21 -1)
//                        e = l21 -1;
//                    break;
//                }
//                else if (l22 < e && l21 > b)
//                {
//                    out.push_back(b);
//                    out.push_back(l21 -1);
//                    b = l22 + 1;
//                    e = ee;
//                    it2 += 2;
//                }
//                else if (l22 >= b && b >= l21)
//                    b = l22 + 1;
//                else if (l21 <= e && e <= l22)
//                {
//                    e = l21 + 1;
//                    break;
//                }
//
//            }
//            if (add)
//            {
//                out.push_back(b);
//                out.push_back(e);
//            }
//        }
//        return out;
//    }
//
//
////    Switch dimensions. When calculating listdiffs between two rows, we can calculate the edges in row direction when
////    row-oriented or in column direction when column-oriented. These edges then give us column-orientation data and vice-versa.
//    void DrcSl::switch_dimensions()
//    {
//        /*
//        **  Switch row to column orientation of the scanlines.
//        **  Example:
//        **
//        **  5: 	[]
//        **  6: 	[]
//        **  7:	[(4,0),(10,1)]
//        **  8:	[(3,0),(7,1),(8,0),(11,1)]
//        **  9:	[(3,0),(8,1),(8,0),(11,1)]
//        **  10:	[(4,0),(8,0),(8,1),(12,1)]
//        **  11:	[(4,0),(7,1)]
//        **  12:	[]
//        **  13:	[]
//        **
//        **  Will be converted to:
//        **
//        **  3:	[]
//        **  4:	[(7,0),(10,1)]
//        **  5:	[(6,0),(12,1)]
//        **  6:	[(6,0),(12,1)]
//        **  7:	[(6,0),(8,1),(8,0),(11,1)]
//        **  8:	[(6,0),(8,1)]
//        **  9:	[(6,0),(11,1)]
//        **  10:	[(7,0),(11,1)]
//        **  11:	[(9,0),(11,1)]
//        **  12:	[]
//        **
//        */
//
////        If progress output is desired uncomment the following lines
////        std::cout << "Switching dimensions" << std::endl;
//        if(this->lhor == nullptr)
//            this->lhor = new std::vector<edgecoord>[this->ver2-this->ver1];
//        if(this->lver == nullptr)
//            this->lver = new std::vector<edgecoord>[this->hor2-this->hor1];
//
//        std::vector<edgecoord> *l_new;
//
//        if (this->orientation)
//        {
//            for(int i = 0; i<this->shor; i++)
//            {
//                this->lhor[i].clear();
//            }
//            l_new = this->lhor;
//        }
//        else
//        {
//            for(int i = 0; i<this->sver; i++)
//            {
//                this->lver[i].clear();
//            }
//            l_new = this->lver;
//        }
//        std::vector<edgecoord> row_last;
//        std::vector<edgecoord> row;
//        std::vector<edgecoord> row_next;
//        std::vector<edgecoord> *it = this->l;
//        std::vector<int>::iterator dit;
//        std::vector<int> dif1;
//        std::vector<int> dif2;
//        std::vector<edgecoord>::iterator rit;
//        row_last = *it;
//        for(rit = row_last.begin(); rit != row_last.end(); rit++)
//        {
//            rit->pos++;
//            rit++;
//            rit->pos--;
//        }
//        it ++;
//        row = *it;
//        for(rit = row.begin(); rit != row.end(); rit++)
//        {
//            rit->pos++;
//            rit++;
//            rit->pos--;
//        }
//        it++;
//        int row_number = 2;
//        for (int n = 2; n < this->s(); n++)
//        {
//            row_next = *it;
//            for(rit = row_next.begin(); rit != row_next.end(); rit++)
//            {
//                rit->pos++;
//                rit++;
//                rit->pos--;
//            }
//
//            dif1 = listdif(row_last,row);
//            dif2 = listdif(row_next,row);
//
//            int b;
//            int e;
//            dit = dif1.begin();
//            while(dit != dif1.end())
//            {
//                b = *dit;
//                dit++;
//                e = *dit;
//                dit++;
//                for (; b!=e+1; b++)
//                {
//                    edgecoord p = edgecoord(row_number-1,1);
//                    l_new[b].push_back(p);
//                }
//            }
//            dit = dif2.begin();
//            while(dit != dif2.end())
//            {
//                b = *dit;
//                dit++;
//                e = *dit;
//                dit++;
//                for (; b!=e+1; b++)
//                {
//                    edgecoord p = edgecoord(row_number-1,0);
//                    l_new[b].push_back(p);
//                }
//            }
//            row_last = row;
//            row = row_next;
//            row_number++;
//            it++;
//        }
//        this->l = l_new;
//        this-> orientation = this->orientation ? hor : ver;
//    }
//
//
////    Function that first cleans space violations then width violations and then space violations again.
////    This does not necessarily clean all violations. For example if a fixing of a width violation creates a space violation
////    and vice-versa, the algorithm will not fix the violation. For performance reasons
////    it is still the user's task to perform DRC and ensure the design is clean. For standard photonic structures it is
////    unlikely that such a case occurs.
//    void DrcSl::clean(int maxtries)
//    {
//        for(int i = 0; i < maxtries; i++)
//        {
//            if(clean_space())
//            {
//                switch_dimensions();
//            }
//            else
//            {
//                if(clean_space())
//                {
//                    switch_dimensions();
//                    continue;
//                }
//                else
//                {
////                    If progress output is desired uncomment the following lines
////                    std::cout<< "Finished after " << i+1 << " tries" << std::endl;
//                    break;
//                }
//            }
//        }
//        for(int i = 0; i < maxtries; i++)
//        {
//            if(clean_width())
//            {
////                If progress output is desired uncomment the following lines
////                std::cout<< "Try: " << i << "/" << maxtries << std::endl;
//                switch_dimensions();
//            }
//            else
//            {
//                if(clean_width())
//                {
//                    switch_dimensions();
//                    continue;
//                }
//                else
//                {
////                    If progress output is desired uncomment the following lines
////                    std::cout<< "Finished after " << i+1 << " tries" << std::endl;
//                    break;
//                }
//            }
//        }
//        for(int i = 0; i < maxtries; i++)
//        {
//            if(clean_space())
//            {
////                If progress output is desired uncomment the following lines
////                std::cout<< "Try: " << i << "/" << maxtries << std::endl;
//                switch_dimensions();
//            }
//            else
//            {
//                if(clean_space())
//                {
//                    switch_dimensions();
//                }
//                else
//                {
//                    if (this->orientation)
//                    {
////                        If progress output is desired uncomment the following lines
////                        std::cout<< "Finished after " << i+1 << " tries" << std::endl;
//                        switch_dimensions();
//                        break;
//                    }
//                }
//            }
//        }
////        If progress output is desired uncomment the following lines
////        std::cout<< "Done cleaning" << std::endl;
//    }
//}//end namespace drclean


