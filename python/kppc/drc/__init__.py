# This file is part of KLayoutPhotonicPcells, an extension for Photonic Layouts in KLayout.
# Copyright (c) 2018, Sebastian Goeldi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""This module uses the C++ submodule :ref:`slcleaner <slcleaner>`. It has to be compiled after installing the
extension.

To compile the module execute the setup script :file:`python/drc/compile.sh`.
Or alternatively execute the :file:`python/kppc/drc/slcleaner_source/setup.py` with the python3 executable
and copy/move the resulting :file:`slcleaner.[...].so` library file ino the :file:`python/drc/` folder.

For further information consult the `Cython Documentation`_.

To execute the script open a console and execute the following commands:

.. code-block:: console

    cd ~/.klayout/salt/KLayoutPhotonicPCells/core/python/kppc/drc
    sh compile.sh

The bash script executes the following commands:

.. literalinclude:: ../../python/kppc/drc/compile.sh
    :language: bash

.. _Cython Documentation: http://cython.org/
"""

import pya

from importlib.util import find_spec

sl_path = find_spec('kppc.drc.slcleaner')

# Check if C++ cleaner is compiled

if not sl_path:
    import os
    import sys

    msg = pya.QMessageBox(pya.Application.instance().main_window())
    msg.text = 'To run the cleaner module, it has to be compiled first. Please execute {}/compile.sh before using the ' \
               'module and reopen KLayout'.format(os.path.dirname(__file__))
    msg.windowTitle = 'ImportError'
    msg.exec_()

#import kppc.drc.slcleaner
#import kppc.drc.cleaner_client
#import kppc.Settings
import kppc
import numpy as np
import time
import sys
import traceback
import os
import subprocess
import signal

qtprogress = True


def clean(cell: 'pya. Cell', cleanrules: list):
    """
    Clean a cell for width and space violations.
    This function will clear the output layers of any shapes and insert a cleaned region.

    :param cell: pointer to the cell that needs to be cleaned
    :param cleanrules: list with the layerpurposepairs, violationwidths and violationspaces in the form [[[layer,
        purpose], violationwidth, violationspace], [[layer2, purpose2], violationwidth2, violationspace2], ...]
    """
    sl = kppc.drc.slcleaner.PyDrcSl()

    if qtprogress:
        progress = pya.RelativeProgress('Cleaning Design Rule Violations', len(cleanrules))

    for cr in cleanrules:

        # split the rules into their parts
        layer_spec, viowidth, viospace = cr
        ln, ld = layer_spec

        if ln is None:
            continue

        layer = cell.layout().layer(ln, ld)

        if qtprogress:
            progress.format = 'Layer {}/{}'.format(ln, ld)

        # Get the bounding box of the layer and initialize the cleaner
        bbox = cell.bbox_per_layer(layer)
        if bbox.empty():
            if qtprogress:
                progress.inc()
            continue
        sl.init_list(bbox.p1.x, bbox.p2.x, bbox.p1.y, bbox.p2.y, viospace, viowidth)

        # Retrieve the recursive
        shapeit = cell.begin_shapes_rec(layer)
        shapeit.shape_flags = pya.Shapes.SPolygons | pya.Shapes.SBoxes

        # feed the data into the cleaner
        reg = pya.Region(shapeit)
        reg.merge()
        for poly in reg.each_merged():
            for edge in poly.each_edge():
                sl.add_data(edge.x1, edge.x2, edge.y1, edge.y2)
        # Sort the edges in an ascending order. Also, removes touching edges or edges within other shapes.
        sl.sort()
        if viowidth != 1 and viospace != 1:
            sl.clean()
        # Create a region from the cleaned data. This is a bit slow. There might be a way to do it faster. The
        # Region merge seems to be the most time consuming process.
        region_cleaned = pya.Region()
        for row in range(bbox.p1.y, bbox.p2.y):
            r = sl.get_row(row)
            if r.size:
                y1 = row
                y2 = row + 1
                for x1, x2 in zip(r[::2], r[1::2]):
                    region_cleaned.insert(pya.Box(int(x1), int(y1), int(x2), int(y2)))
        region_cleaned.merge()

        # Clean the target layer and fill in the cleaned data
        cell.clear(layer)
        cell.shapes(layer).insert(region_cleaned)
        if qtprogress:
            progress.inc()
    progress._destroy()


def multiprocessing_clean(cell: 'pya. Cell', cleanrules: list):
    """
    Clean a cell for width and space violations.
    This function will clear the output layers of any shapes and insert a cleaned region.

    :param cell: pointer to the cell that needs to be cleaned
    :param cleanrules: list with the layerpurposepairs, violationwidths and violationspaces in the form [[[layer,
        purpose], violationwidth, violationspace], [[layer2, purpose2], violationwidth2, violationspace2], ...]
    """
   # print("Multiprocessed Cleaning started")
   
    t = time.time()

    cc = kppc.drc.cleaner_client.PyCleanerClient()
    ce = subprocess.Popen([os.path.dirname(os.path.abspath(__file__))+'/cleaner_engine'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    if qtprogress:
        progress = pya.RelativeProgress('Cleaning Design Rule Violations', len(cleanrules))

    try:

        count = 0

        #print(cleanrules)

        for cr in cleanrules:

            # split the rules into their parts
            layer_spec, viowidth, viospace = cr
            ln, ld = layer_spec

            if ln is None:
                continue

            layer = cell.layout().layer(ln, ld)

            if qtprogress:
                progress.format = 'Layer {}/{}'.format(ln, ld)

            # Get the bounding box of the layer and initialize the cleaner
            bbox = cell.bbox_per_layer(layer)
            if bbox.empty() or np.abs(bbox.p1.x - bbox.p2.x) < viowidth or np.abs(bbox.p1.y - bbox.p2.y) < viowidth:
                if qtprogress:
                    progress.inc()
                continue
            else:

                processing = cc.set_box(ln, ld, viowidth, viospace, bbox.p1.x, bbox.p2.x, bbox.p1.y, bbox.p2.y)
                # Retrieve the recursive
                shapeit = cell.begin_shapes_rec(layer)
                shapeit.shape_flags = pya.Shapes.SPolygons | pya.Shapes.SBoxes

                # feed the data into the cleaner
                reg = pya.Region(shapeit)
                reg.merge()
                for poly in reg.each_merged():
                    for edge in poly.each_edge():
                        cc.add_edge(edge.x1, edge.x2, edge.y1, edge.y2)
                while (cc.done()):
                    time.sleep(.1)

                count += 1

        for i in range(count):
            while (True):
                #print("Poly")
                lines = cc.get_layer()
                #print(type(lines))
                waiting = np.all(lines[0] == [-1, -1])
                if waiting:
                    time.sleep(.1)
                    continue
                else:
                    layer = cell.layout().layer(lines[0][0],lines[0][1])
                    
                    #region_cleaned = pya.Region()
                    bbox = cell.bbox_per_layer(layer)
                    
                    region_cleaned = pya.Region()
                    for row in range(bbox.p1.y, bbox.p2.y):
                        r = lines[row - bbox.p1.y + 1]
                        if len(r):
                            y1 = row
                            y2 = row + 1
                            for x1, x2 in zip(r[::2], r[1::2]):
                                region_cleaned.insert(pya.Box(int(x1), int(y1), int(x2), int(y2)))
                    #region_cleaned.merge()
                    
                    #print(len(polygons))
                    #for poly in polygons[1:]:
                    #    points = []
                    #    for i in range(len(poly)//2):
                    #        points.append(pya.Point(poly[i*2],poly[i*2+1]))
                    #    region_cleaned.insert(pya.Polygon(points))
                            
                    region_cleaned.merge()
            
                    # Clean the target layer and fill in the cleaned data
                    cell.clear(layer)
                    cell.shapes(layer).insert(region_cleaned)
                    if qtprogress:
                        progress.inc()
                    break

    except Exception as e:
        print("whoops")
        print(e)
        traceback.print_exc(file=sys.stdout)

        '''sl.init_list(bbox.p1.x, bbox.p2.x, bbox.p1.y, bbox.p2.y, viospace, viowidth)

        # Retrieve the recursive
        shapeit = cell.begin_shapes_rec(layer)
        shapeit.shape_flags = pya.Shapes.SPolygons | pya.Shapes.SBoxes

        # feed the data into the cleaner
        reg = pya.Region(shapeit)
        reg.merge()
        for poly in reg.each_merged():
            for edge in poly.each_edge():
                sl.add_data(edge.x1, edge.x2, edge.y1, edge.y2)
        # Sort the edges in an ascending order. Also, removes touching edges or edges within other shapes.
        sl.sort()
        if viowidth != 1 and viospace != 1:
            sl.clean()
        # Create a region from the cleaned data. This is a bit slow. There might be a way to do it faster. The
        # Region merge seems to be the most time consuming process.
        region_cleaned = pya.Region()
        for row in range(bbox.p1.y, bbox.p2.y):
            r = sl.get_row(row)
            if r.size:
                y1 = row
                y2 = row + 1
                for x1, x2 in zip(r[::2], r[1::2]):
                    region_cleaned.insert(pya.Box(int(x1), int(y1), int(x2), int(y2)))
        region_cleaned.merge()

        # Clean the target layer and fill in the cleaned data
        cell.clear(layer)
        cell.shapes(layer).insert(region_cleaned)
        if qtprogress:
            progress.inc()'''
    finally:
        print("Done. Time passed")
        print(time.time()-t)
        progress._destroy()
        ce.send_signal(signal.SIGUSR1)
        ce.wait()
        

    print("Multiprocessed Cleaning done " + str(ln) + "/" + str(ld))
