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
from pathlib import Path
import kppc
import numpy as np
import time
import sys
import traceback
import os
import subprocess
import signal

from importlib.util import find_spec

dir_path = Path(__file__).parent
sl_path = find_spec('kppc.drc.slcleaner')
can_multi = find_spec('kppc.drc.cleanermaster') and Path(dir_path / 'cleanermain').exists()

# Check if C++ cleaner is compiled

if not sl_path:
    msg = pya.QMessageBox(pya.Application.instance().main_window())
    msg.text = 'To run the cleaner module, it has to be compiled first. Please execute {}/compile_cc.sh before using' \
               'the module and reopen KLayout'.format(dir_path)
    msg.windowTitle = 'ImportError'

    compile_button = msg.addButton("Automatic Compilation", pya.QMessageBox.ButtonRole.NoRole)
    msg.addButton(pya.QMessageBox.StandardButton.Abort)

    msg.exec_()
    print(msg.clickedButton())

    if msg.clickedButton() == compile_button:
        src_dir = dir_path / "slcleaner_source"
        print('Trying to Compile')
        p1 = subprocess.Popen(['python3', 'setup.py', 'build_ext', '-b', '../'], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, cwd=src_dir)
        p2 = subprocess.Popen(['python3', 'setup_cc.py', 'build_ext', '-b', '../'], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, cwd=src_dir)
        p3 = subprocess.Popen(
            ['g++', 'CleanerMain.cpp', 'CleanerSlave.cpp', 'DrcSl.cpp', 'SignalHandler.cpp', '-o', '../cleanermain', '-isystem',
             '/usr/include/boost/', '-lboost_system', '-pthread', '-lboost_thread', '-lrt'], stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, cwd=src_dir)
        p1.wait()
        p2.wait()
        p3.wait()
        if p1.returncode == 0 and p2.returncode == 0 and p3.returncode == 0:
            msg = pya.QMessageBox(pya.Application.instance().main_window())
            msg.text = 'The compilation was successfull'
            msg.Title = 'Compilation'
            can_multi = find_spec('kppc.drc.cleanermaster') and Path(dir_path / 'cleanermain').exists()
            msg.exec_()
        else:
            msg = pya.QMessageBox(pya.Application.instance().main_window())
            msg.text = 'The compilation failed. Please compile manually'
            msg.Title = 'Compilation'
            msg.exec_()
            exit(-1)
    else:
        exit(-1)

else:
    import kppc.drc.slcleaner

if not can_multi:
    print("Cannot use mutliprocessing, falling back to single thread cleaning")
    kppc.settings.multiprocessing = False
else:
    import kppc.drc.cleanermaster


def clean(cell: 'pya. Cell', cleanrules: list):
    """
    Clean a cell for width and space violations.
    This function will clear the output layers of any shapes and insert a cleaned region.

    :param cell: pointer to the cell that needs to be cleaned
    :param cleanrules: list with the layerpurposepairs, violationwidths and violationspaces in the form [[[layer,
        purpose], violationwidth, violationspace], [[layer2, purpose2], violationwidth2, violationspace2], ...]
    """
    sl = kppc.drc.slcleaner.PyDrcSl()

    if kppc.settings.qtprogress:
        progress = pya.RelativeProgress('Cleaning Design Rule Violations', len(cleanrules))

    for cr in cleanrules:

        # split the rules into their parts
        layer_spec, viowidth, viospace = cr
        ln, ld = layer_spec

        if ln is None:
            continue

        layer = cell.layout().layer(ln, ld)

        if kppc.settings.qtprogress:
            progress.format = 'Layer {}/{}'.format(ln, ld)

        # Get the bounding box of the layer and initialize the cleaner
        bbox = cell.bbox_per_layer(layer)
        if bbox.empty():
            if kppc.settings.qtprogress:
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
        if kppc.settings.qtprogress:
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

    cm = kppc.drc.cleanermaster.PyCleanerMaster()
    cs = subprocess.Popen([os.path.dirname(os.path.abspath(__file__)) + '/cleanermain'], stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)

    if kppc.settings.qtprogress:
        progress = pya.RelativeProgress('Cleaning Design Rule Violations', len(cleanrules))

    try:

        count = 0

        for cr in cleanrules:

            # split the rules into their parts
            layer_spec, viowidth, viospace = cr
            ln, ld = layer_spec

            if ln is None:
                continue

            layer = cell.layout().layer(ln, ld)

            if kppc.settings.qtprogress:
                progress.format = 'Layer {}/{}'.format(ln, ld)

            # Get the bounding box of the layer and initialize the cleaner
            bbox = cell.bbox_per_layer(layer)
            if bbox.empty() or np.abs(bbox.p1.x - bbox.p2.x) < viowidth or np.abs(bbox.p1.y - bbox.p2.y) < viowidth:
                if kppc.settings.qtprogress:
                    progress.inc()
                continue
            else:

                cm.set_box(ln, ld, viowidth, viospace, bbox.p1.x, bbox.p2.x, bbox.p1.y, bbox.p2.y)
                print("Initialized Layer {}/{}".format(ln,ld))
                # Retrieve the recursive
                shapeit = cell.begin_shapes_rec(layer)
                shapeit.shape_flags = pya.Shapes.SPolygons | pya.Shapes.SBoxes

                # feed the data into the cleaner
                reg = pya.Region(shapeit)
                reg.merge()
                for poly in reg.each_merged():
                    for edge in poly.each_edge():
                        cm.add_edge(edge.x1, edge.x2, edge.y1, edge.y2)
                while cm.done():
                    time.sleep(.1)

                count += 1
                
        for i in range(count):
            while True:
                polygons = cm.polygons()
                waiting = np.all(polygons[0][0] == (-1, -1))
                if waiting:
                    time.sleep(1)
                    continue
                else:
                    layer = cell.layout().layer(polygons[0][0][0], polygons[0][0][1])
                    bbox = cell.bbox_per_layer(layer)

                    region_cleaned = pya.Region()
                    for p in polygons[1:]:
                        region_cleaned.insert(pya.Polygon([pya.Point(x[0],x[1]) for x in p]))
                    region_cleaned.merge()

                    # Clean the target layer and fill in the cleaned data
                    cell.clear(layer)
                    cell.shapes(layer).insert(region_cleaned)
                    if kppc.settings.qtprogress:
                        progress.inc()
                    break

    except Exception as e:
        print(e)
        traceback.print_exc(file=sys.stdout)
    finally:
        print("Done. Time passed: {}".format(time.time() - t))
        progress._destroy()
        cs.send_signal(signal.SIGUSR1)
        cs.wait()
        
        
#def merge_layer_from_shared_memory():
#    cm = kppc.drc.cleaner_client.PyCleanerClient()
#    layout = pya.Layout()
#    cell = layout.create_cell("TOP")
#    while True:
#        lines = cm.get_layer()
#        waiting = np.all(lines[0] == [-1, -1])
#        if waiting:
#            time.sleep(.1)
#            continue
#        else:
#            layer = cell.layout().layer(lines[0][0], lines[0][1])
#
#            bbox = cell.bbox_per_layer(layer)
#
#            region_cleaned = pya.Region()
#            for row in range(len(lines)-1):
#                r = lines[row+1]
#                if len(r):
#                    y1 = row
#                    y2 = row + 1
#                    for x in range(0,len(r),2):
#                    #zip(r[::2], r[1::2])
#                        region_cleaned.insert(pya.Box(int(r[x]), int(y1), int(r[x+1]), int(y2)))
#
#            region_cleaned.merge()
#
#            # Clean the target layer and fill in the cleaned data
#            cell.clear(layer)
#            cell.shapes(layer).insert(region_cleaned)
#            break
#    layout.save("{}/{}.gds".format(layer,datatype))

    