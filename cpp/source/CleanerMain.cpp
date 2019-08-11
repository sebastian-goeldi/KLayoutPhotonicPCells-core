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
#include <string>

int main(int argc, char* argv[])
{
    drclean::CleanerSlave* cs;
    if(argc < 2)
    {
        cs = new drclean::CleanerSlave();
    } else if(argc == 2) {
        cs = new drclean::CleanerSlave(std::stoi(argv[1]));
    }
    
    
    if (!cs->initialized)
    {
        return -1;
    }

    SignalHandler signalHandler;
    signalHandler.setSignalToHandle(SIGUSR1);

    while(!signalHandler.isSignalSet())
    {
        cs->clean();
    }

//     Cleanup
    cs->join_threads();
    delete cs;

    return 0;
}
