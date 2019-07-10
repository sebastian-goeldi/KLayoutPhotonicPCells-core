//  This file is part of KLayout-photonics, an extension for Photonic Layouts in KLayout.
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

#include "EdgeCleaner.h"


namespace drclean{

    EdgeCleaner::initialize(int x1, int x2, int y1, int y2)
    {
        if(x2<=x1 || y2<=y1)
            throw "Zero or negative Size";
        this->begin = new Edge(x1,y1,y2,LEFT);
        this->end = new Edge(x2,y1,y2,RIGHT);
    }

    EdgeCleaner::add_edge(int x, int y1, int y2, int type)
    {
        Edge* e = Edge(x,y1,y2,type)
        for(auto i: this->edges_by_x)
        {
            if(i==this->edges_by_x.end() || (x == i->x && y1 < i->y1) || x > t->x )
            {
                this->edges_by_x.insert(i,e);
                break;
            }
        }
        for(auto i: this->edges_by_y1)
        {
            if(i==this->edges_by_y1.end() || (y1 == i->y1 && x < i->x) || y1 > i->y1 )
            {
                this->edges_by_y1.insert(i,e);
                break;
            }
        }
        for(auto i: this->edges_by_y2)
        {
            if(i==this->edges_by_y2.end() || (y2 == y2->x && x < i->x) || y2 > i->y2 )
            {
                this->edges_by_y2.insert(i,e);
                break;
            }
        }

        for(auto i; (*i)->)
//        std::vector<Edge>::iterator e1;
//        std::vector<Edge>::iterator e2;
//
//        e2 = this->next;
//        for (e1: this->next)
//        {
//            int overl = e->overlaps(x,y1,y2)
//            if(overl == 2)
//            {
//            }
//            elseif(overl)
//            {
////                TODO add partial edge
//            }
//        }
    }

    EdgeCleaner::clean()
    {
        for(auto e: left)

    }

}