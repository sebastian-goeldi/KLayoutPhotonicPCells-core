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

#ifndef DRCSL_H
#define DRCSL_H


#include <vector>
#include <algorithm>


namespace drclean{

    enum orientation
    {
        hor = 0,
        ver = 1,
    };

    struct edgecoord {
        /*
        **  Struct to store information about an edge and it's dimensions.
        **  @pos: The coordinate of an edge.
        **  @type:The type of an edge.  0: Polygon is in the positive coordinate direction from the edge.
        **                              1: Polygon is in the negative coordinate direction from the edge.
        */

        int pos;
        int type;
        bool rem = false;
        edgecoord(int p, int t, bool r = false): pos(p), type(t), rem(r) {};
        ~edgecoord(){};
    };


    class DrcSl
    {
        public:
            DrcSl();
            //DrcSl(std::vector<std::vector<edgecoord>> horlist, int s);

            ~DrcSl();

            int set_data(std::vector<edgecoord> *horlist);
            void initialize_list(int hor1,int hor2, int ver1, int ver2, int violation_space, int violation_width);
            void sortlist();
            void add_data(int hor1,int hor2, int ver1, int ver2);
            bool list_cleaning();
            int clean_space();
            int clean_width();
            void switch_dimensions();
            void read_from_file(char* filename);
            void write_to_file(char* filename);
            std::vector<int> get_vect(int ind);
            std::vector<int> get_types(int ind);
            void clean(int max_tries = 10);
            void define_edges(std::vector<edgecoord> *l);
            int violation_width;
            int violation_space;
            void printvector(int beg = -1, int ende = -1);
            int hor1;
            int hor2;
            int ver1;
            int ver2;
            int s();
            std::vector<edgecoord> *l;


        protected:
            std::vector<int> listdif(std::vector<edgecoord> &l1,std::vector<edgecoord> &l2);

        private:
            int i;
            bool orientation = hor; //0 -> row representation , 1 -> column representation
            std::vector<edgecoord> *lhor;
            std::vector<edgecoord> *lver;
            int shor;
            int sver;
    };


}

#endif // DRCSL_H
