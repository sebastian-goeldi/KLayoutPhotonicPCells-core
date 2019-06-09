#include <boost/interprocess/managed_shared_memory.hpp>

namespace bi = boost::interprocess;


int main(int argc, char* argv[])
{
    bi::shared_memory_object::remove("DRCleanEngine");
}
