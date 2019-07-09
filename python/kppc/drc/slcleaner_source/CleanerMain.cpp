#include "CleanerSlave.h"

int main(int argc, char* argv[])
{

    std::cout<< "Initializing" << std::endl;
    drclean::CleanerSlave cs = drclean::CleanerSlave();

    std::cout<< "Initialized" << std::endl;

    if (!cs.initialized)
    {
        return -1;
    }

    SignalHandler signalHandler;
    signalHandler.setSignalToHandle(SIGUSR1);

    while(!signalHandler.isSignalSet())
    {
        cs.clean();
    }
}