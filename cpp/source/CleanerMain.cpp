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

    cs.join_threads();


    return 0;
}