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

To compile the module execute the setup script :file:`scripts/compile.sh`.
Or alternatively execute the :file:`python/kppc/drc/slcleaner_source/setup.py` with the python3 executable
and copy/move the resulting :file:`slcleaner.[...].so` library file ino the :file:`python/drc/` folder.

For further information consult the `Cython Documentation`_.

To execute the script open a console and execute the following commands:

.. code-block:: console

    cd ~/.klayout/salt/KLayoutPhotonicPCells/core/scripts
    sh compile.sh

The bash script executes the following commands:

.. literalinclude:: ../../../scripts/clean_compile.sh
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
import subprocess
import signal
import multiprocessing

from importlib.util import find_spec

dir_path = Path(__file__).parent
cpp_path = dir_path.parent.parent.parent / "cpp"
sl_path = find_spec('kppc.drc.slcleaner')
can_multi = find_spec('kppc.drc.cleanermaster') and Path(
    cpp_path / 'build/cleanermain').exists() and kppc.settings.Multithreading.Enabled

# Check if C++ cleaner is compiled

if not sl_path:
    msg = pya.QMessageBox(pya.Application.instance().main_window())
    msg.text = 'To run the cleaner module, it has to be compiled first. Please execute {}/compile_cc.sh before using' \
               'the module and reopen KLayout'.format(dir_path)
    msg.windowTitle = 'ImportError'

    compile_button = msg.addButton("Automatic Compilation", pya.QMessageBox.ButtonRole.NoRole)
    msg.addButton(pya.QMessageBox.StandardButton.Abort)

    msg.exec_()

    if msg.clickedButton() == compile_button:
        src_dir = cpp_path / "source"
        print('Trying to Compile')

        (cpp_path / 'build').mkdir(parents=True, exist_ok=True)

        p1 = subprocess.Popen(['python3', 'setup.py', 'build_ext', '-b', dir_path], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, cwd=src_dir)
        p2 = subprocess.Popen(['python3', 'setup_cc.py', 'build_ext', '-b', dir_path], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, cwd=src_dir)
        p3 = subprocess.Popen(
            ('g++', cpp_path / 'source/CleanerMain.cpp', cpp_path / 'source/CleanerSlave.cpp',
             cpp_path / 'source/DrcSl.cpp', cpp_path / 'source/SignalHandler.cpp', '-o', cpp_path / 'build/cleanermain',
             '-isystem',
             '/usr/include/boost/', '-lboost_system', '-pthread', '-lboost_thread', '-lrt'), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, cwd=src_dir)
        p1.wait()
        p2.wait()
        p3.wait()
        if p1.returncode == 0 and p2.returncode == 0 and p3.returncode == 0:
            msg = pya.QMessageBox(pya.Application.instance().main_window())
            msg.text = 'The compilation was successful'
            msg.Title = 'Compilation'
            can_multi = find_spec('kppc.drc.cleanermaster') and Path(dir_path / 'cleanermain').exists()
            msg.exec_()
            import kppc.drc.slcleaner
        else:
            msg = pya.QMessageBox(pya.Application.instance().main_window())
            msg.text = 'The compilation failed. Please compile manually\n Return Code slcleaner: {}\n Return Code ' \
                       'cleanermaster: {}\n Return Code: {}\n}'.format(p1.returncode, p2.returncode, p3.returncode)
            msg.Title = 'Compilation'
            msg.exec_()
            exit(-1)
    else:
        exit(-1)

else:
    import kppc.drc.slcleaner

if not can_multi:
    print("Cannot use multiprocessing, falling back to single thread cleaning")
    kppc.settings.Multithreading.Enabled = False
else:
    print("Using the multiprocessing module")

if find_spec('kppc.drc.cleanermaster') and Path(cpp_path / 'build/cleanermain').exists():
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

    if kppc.settings.General.Progressbar:
        progress = pya.RelativeProgress('Cleaning Design Rule Violations', len(cleanrules))

    for cr in cleanrules:

        # split the rules into their parts
        layer_spec, violation_width, violation_space = cr
        ln, ld = layer_spec

        if ln is None:
            continue

        layer = cell.layout().layer(ln, ld)

        if kppc.settings.General.Progressbar:
            progress.format = 'Layer {}/{}'.format(ln, ld)

        # Get the bounding box of the layer and initialize the cleaner
        bbox = cell.bbox_per_layer(layer)
        if bbox.empty():
            if kppc.settings.General.Progressbar:
                progress.inc()
            continue
        sl.init_list(bbox.p1.x, bbox.p2.x, bbox.p1.y, bbox.p2.y, violation_space, violation_width)

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
        if violation_width != 1 and violation_space != 1:
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
        if kppc.settings.General.Progressbar:
            progress.inc()
    if kppc.settings.General.Progressbar:
        progress._destroy()


def multiprocessing_clean(cell: 'pya. Cell', cleanrules: list):
    """
    Clean a cell for width and space violations.
    This function will clear the output layers of any shapes and insert a cleaned region.
    Does the cleaning in a seperate Process started as a childprocess,
    which will calculate in parallel with multiple threads.

    :param cell: pointer to the cell that needs to be cleaned
    :param cleanrules: list with the layerpurposepairs, violationwidths and violationspaces in the form [[[layer,
        purpose], violationwidth, violationspace], [[layer2, purpose2], violationwidth2, violationspace2], ...]
    """
    t = time.time()

    cm = kppc.drc.cleanermaster.PyCleanerMaster()
    if kppc.settings.Multithreading.Automatic:
        cs = subprocess.Popen([cpp_path / 'build/cleanermain', ], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
    else:
        n = kppc.settings.Multithreading.Threads
        if n < 1:
            n = 1
        elif n > multiprocessing.cpu_count():
            n = multiprocessing.cpu_count()
        cs = subprocess.Popen([cpp_path / 'build/cleanermain', str(n), ],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)

    if kppc.settings.General.Progressbar:
        processedlayers = {}
        for cr in cleanrules:
            layer_spec, violation_width, violation_space = cr
            ln, ld = layer_spec
            processedlayers['{}/{}'.format(ln, ld)] = False

        progress = pya.RelativeProgress('Preparing Output Layers', len(cleanrules))
        progress.format = 'Processed {} of {} layers'.format(0, len(cleanrules))

    try:
        len_cr = len(cleanrules)
        count = 0
        skip = 0

        for cr in cleanrules:

            # split the rules into their parts
            layer_spec, violation_width, violation_space = cr
            ln, ld = layer_spec

            if ln is None:
                continue

            layer = cell.layout().layer(ln, ld)

            # Get the bounding box of the layer and initialize the cleaner
            bbox = cell.bbox_per_layer(layer)
            if bbox.empty() or np.abs(bbox.p1.x - bbox.p2.x) < violation_width or np.abs(
                    bbox.p1.y - bbox.p2.y) < violation_width:
                skip += 1
                if kppc.settings.General.Progressbar:
                    progress.format = 'Processed {} of {} Output Layers and scheduled for Cleaning'.format(
                        count + skip, len_cr)
                    progress.inc()
                continue
            else:

                cm.set_box(ln, ld, violation_width, violation_space, bbox.p1.x, bbox.p2.x, bbox.p1.y, bbox.p2.y)
                # Retrieve the recursive
                shapeit = cell.begin_shapes_rec(layer)
                shapeit.shape_flags = pya.Shapes.SPolygons | pya.Shapes.SBoxes

                # Feed the data into the cleaner
                reg = pya.Region(shapeit)
                reg.merge()
                for poly in reg.each_merged():
                    for edge in poly.each_edge():
                        cm.add_edge(edge.x1, edge.x2, edge.y1, edge.y2)
                while cm.done():
                    time.sleep(.1)

                count += 1

            if kppc.settings.General.Progressbar:
                progress.format = 'Processed {} of {} Output Layers and scheduled for Cleaning'.format(count + skip,
                                                                                                       len_cr)
                progress.inc()

        if kppc.settings.General.Progressbar:
            progress._destroy()
            progress = pya.RelativeProgress('Cleaning Design Rule Violations', count)
            progress.format = 'Cleaned Violations in {} of {} Layers. Next expected layer: {}'.format(0, count, next(
                (x for x in processedlayers.keys() if not processedlayers[x]), None))

        for i in range(count):
            while True:
                polygons = cm.polygons()
                waiting = np.all(polygons[0][0] == (-1, -1))
                if waiting:
                    time.sleep(1)
                    continue
                else:
                    ln, ld = polygons[0][0][0], polygons[0][0][1]
                    layer = cell.layout().layer(ln, ld)
                    bbox = cell.bbox_per_layer(layer)

                    region_cleaned = pya.Region()
                    for p in polygons[1:]:
                        region_cleaned.insert(pya.Polygon([pya.Point(x[0], x[1]) for x in p]))
                    region_cleaned.merge()

                    # Clean the target layer and fill in the cleaned data
                    cell.clear(layer)
                    cell.shapes(layer).insert(region_cleaned)
                    if kppc.settings.General.Progressbar:
                        processedlayers['{}/{}'.format(ln, ld)] = True
                        text = 'Cleaned Violations in {} of {} Layers. Next expected layer: {}'
                        text.format(i + 1, count,
                                    next((x for x in processedlayers.keys() if not processedlayers[x]), None))
                        progress.format = text
                        progress.inc()
                    break

    except Exception as e:
        print(e)
        traceback.print_exc(file=sys.stdout)
    finally:
        print("Done. Time passed: {}".format(time.time() - t))
        cs.send_signal(signal.SIGUSR1)
        cs.wait()
        if kppc.settings.General.Progressbar:
            progress._destroy()
