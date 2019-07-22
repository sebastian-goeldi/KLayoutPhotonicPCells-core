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
#ifndef DRCSL_H
#define DRCSL_H


#include <vector>
#include <algorithm>
#include <iostream>

typedef std::pair<int,int> pi;



namespace drclean
{


struct SplitPolygon
{

public:
    std::vector<pi>* left;
    std::vector<pi>* right;
    std::vector<std::vector<SplitPolygon>::iterator> *merge_to;
    SplitPolygon():merged(false),passed(false)
    {
        right = new std::vector<pi>();
        left = new std::vector<pi>();
        merge_to = new std::vector<std::vector<SplitPolygon>::iterator>();
    };
//            ~SplitPolygon(){
//                delete right;
//                delete left;
//                delete merge_to;
//            }
    int can_append(int x1, int x2, int l)
    {
        if (l != line +1 )
            return 0;
        if(x2 < left->back().first)
            return 1;
        if(x1 > right->back().second)
            return -1;
        return 2;
    }
    void init(int x1, int x2, int l)
    {
        left->push_back(std::make_pair(x1,l));
        left->push_back(std::make_pair(x1,l+1));
        right->push_back(std::make_pair(x2,l));
        right->push_back(std::make_pair(x2,l+1));
        line = l+1;
        lx = x1;
        rx = x2;
    }

    int append(int x1, int x2, int l)
    {
        if(x1 == left->back().first)
        {
            left->back().second++;
        }
        else
        {
            left->push_back(std::make_pair(x1,l));
            left->push_back(std::make_pair(x1,l+1));
        }

        if(x2 == right->back().first)
        {
            right->back().second++;
        }
        else
        {
            right->push_back(std::make_pair(x2,l));
            right->push_back(std::make_pair(x2,l+1));
        }
        line = l+1;
        lx = x1;
        rx = x2;
        return true;
    }
    void right_insert(std::vector<pi> polygon)
    {
        right->insert(right->end(),polygon.begin(),polygon.end());
    }
    void right_merge()
    {
        right->insert(right->end(),left->rbegin(),left->rend());
        left->clear();
    }

    int line;
    int lx,rx;

    bool merged;
    bool passed;
};

typedef std::vector<SplitPolygon> spv;

enum orientation
{
    hor = 0,
    ver = 1,
};

struct edgecoord
{
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
    virtual ~edgecoord() {};
};


typedef std::vector<edgecoord> ev;


class DrcSl
{
public:
    DrcSl();
    ~DrcSl();

    int set_data(std::vector<edgecoord> *horlist);
    void initialize_list(int hor1,int hor2, int ver1, int ver2, int violation_space, int violation_width);
    void sortlist();
    void add_data(int hor1,int hor2, int ver1, int ver2);
    bool list_cleaning();
    int clean_space();
    int clean_width();
    void switch_dimensions();
    std::vector<int> get_vect(int ind);
    std::vector<int> get_types(int ind);
    void clean(int max_tries = 10);
    int violation_width;
    int violation_space;
    void printvector(int beg = -1, int ende = -1);
    int hor1;
    int hor2;
    int ver1;
    int ver2;
    int s();
    std::vector<edgecoord> *l;
    std::vector<std::vector<int>> get_lines();
    std::vector<std::vector<pi>> get_polygons();

protected:
    std::vector<int> listdif(std::vector<edgecoord> &l1,std::vector<edgecoord> &l2);

private:
    int i;
    bool orientation = hor; //0 -> row representation , 1 -> column representation
    std::vector<edgecoord> *lhor;
    std::vector<edgecoord> *lver;
    int shor;
    int sver;
    std::vector<std::vector<pi>> polygons;
    std::vector<SplitPolygon> splits;

};


}

#endif // DRCSL_H
