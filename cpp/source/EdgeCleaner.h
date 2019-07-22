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

#ifndef EDGECLEANER_H
#define EDGECLEANER_H


#include <vector>
#include <algorithm>

namespace drclean{

    enum orientation
    {
        HOR = 0,
        VER = 1,
    };

    enum edgelr
    {
        LEFT = 0;
        RIGHT = 1;
    }

    struct Point
    {
        int x;
        int y;
        Point(int i, int j){x=i;y=j}
        ~Point(){};
    }

    struct PartialPolygon
    {
        int minx;
        int maxx;
        int miny;
        int maxy;
        std::vector<int> left;
        std::vector<int> right;

        bool can_merge(std::vector<int>::iterator it1,std::vector<int>::iterator it2)
        {return(!(*it2 < left.back() || *it1 > right.back()));}
        void add(int l, int r)
        {left.push_back(l);right.push_back(r);}
        leftpolygonize()
        {
            for(std::vector<int>::iterator iter = right.rbegin(); iter!= right.rend();iter+=2)
            {
                left.push_back(*(iter+1));
                left.push_back(*(iter));
            }
        }
        rightpolygonize()
        {
            for(std::vector<int>::iterator iter = left.rbegin(); iter!= left.rend();iter+=2)
            {
                right.push_back(*(iter+1));
                right.push_back(*(iter));
            }
        }

    };

    struct coordinate {
        int x;
        int y;
    };

    struct Edge {
        /*
        **  Struct to store information about an edge and it's dimensions.
        **  @pos: The coordinate of an edge.
        **  @type:The type of an edge.  0: Polygon is in the positive coordinate direction from the edge.
        **                              1: Polygon is in the negative coordinate direction from the edge.
        */

        int x;
        int y1;
        int y2;
        int type;
        Edge(x,y1,y2,type){
            Edge::x = x;
            if(y2 < y1){
                Edge::y1 = y2;Edge::y2=y1;
            }
            else {
                Edge::y2 = y1;Edge::y2=y2;
            }
            Edge::type=type;
        };
        Edge(){};
        std::vector<Edge*> next;
        int overlaps(int y1, int y2)
        {
            if(Edge::y2 >= y2 && Edge::y1<=y1)
            {return 2;}
            else
            {return(y1<Edge::y2 && y2>Edge::y1)}
        }
    };

    struct EdgeSpan {

        int y1;
        int y2;
        Edge * edge;

        compare(int a, int b) {return(!(b < y1 || a > y2));}
    }


    class EdgeCleaner
    {
        public:
            EdgeCleaner();
            //DrcSl(std::vector<std::vector<edgecoord>> horlist, int s);

            ~EdgeCleaner();

            Edge* begin;
            Edge* end;
            Edge* top;
            std::vector<Edge*> edges_by_x;
            std::vector<Edge*> edges_by_y1;
            std::vector<Edge*> edges_by_y2;


            void initialize(int x1, int x2, int y1, int y2);
            void add_edge(int x, int y1, int y2);
            void rotate();

        protected:
            std::vector<Edge*> edges;

        private:


    };


}

#endif // EDGECLEANER_H
