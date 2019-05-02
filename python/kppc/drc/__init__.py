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
    msg.text = 'To run the cleaner module, it has to be compiled first. Please execute {}/compile.sh before using the module and reopen KLayout'.format(
        os.path.dirname(__file__))
    msg.windowTitle = 'ImportError'
    msg.exec_()

import kppc.drc.slcleaner

qtprogress = True


class ThreadedCleaner(pya.QThread):

    def __init__(self, cr, cell, progress=None):
        self.cr = cr
        self.cell = cell
        self.progress = progress
        pya.QThread.__init()
        # kppc.drc.slcleaner.PyDrcSl.__init__()

    def run(self):
        sl = kppc.drc.slcleaner.PyDrcSl()

        # split the rules into their parts
        layer_spec, viowidth, viospace = self.cr
        ln, ld = layer_spec

        if ln is None:
            if qtprogress:
                self.progress.inc()
            return

        layer = self.cell.layout().layer(ln, ld)

        if qtprogress:
            self.progress.format = 'Layer {}/{}'.format(ln, ld)

        # Get the bounding box of the layer and initialize the cleaner
        bbox = self.cell.bbox_per_layer(layer)
        if bbox.empty():
            if qtprogress:
                self.progress.inc()
            return
        sl.init_list(bbox.p1.x, bbox.p2.x, bbox.p1.y, bbox.p2.y, viospace, viowidth)

        # Retrieve the recursive
        shapeit = self.cell.begin_shapes_rec(layer)
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
        self.cell.clear(layer)
        self.cell.shapes(layer).insert(region_cleaned)
        if qtprogress:
            self.progress.inc()


def clean(cell: 'pya. Cell', clean_rules: list):
    """
    Clean a cell for width and space violations.
    This function will clear the output layers of any shapes and insert a cleaned region.

    :param cell: pointer to the cell that needs to be cleaned
    :param clean_rules: list with the layerpurposepairs, violationwidths and violationspaces in the form [[[layer,
        purpose], violationwidth, violationspace], [[layer2, purpose2], violationwidth2, violationspace2], ...]
    """

    print("Cleaning :D")

    if qtprogress:
        progress = pya.RelativeProgress('Cleaning Design Rule Violations', len(clean_rules))
    else:
        progress = None

    app = pya.QApplication()

    threadpool = []

    print("Creating Threads")

    for cr in clean_rules:
        threadpool.append(ThreadedCleaner(cr, cell, progress))
        print("Thread created")

    print("All threads created")

    for th in threadpool:
        th.run()
        print("Started thread")

    print("Started all threads")

    print("Waiting for threads to finish")

    for th in threadpool:
        th.wait()
        print("Thread finished")

    print("All threads finished")

    app.exec()

    #
    #     sl = kppc.drc.slcleaner.PyDrcSl()
    #
    #     # split the rules into their parts
    #     layer_spec, viowidth, viospace = cr
    #     ln, ld = layer_spec
    #
    #     if ln is None:
    #         continue
    #
    #     layer = cell.layout().layer(ln, ld)
    #
    #     if qtprogress:
    #         progress.format = 'Layer {}/{}'.format(ln, ld)
    #
    #     # Get the bounding box of the layer and initialize the cleaner
    #     bbox = cell.bbox_per_layer(layer)
    #     if bbox.empty():
    #         if qtprogress:
    #             progress.inc()
    #         continue
    #     sl.init_list(bbox.p1.x, bbox.p2.x, bbox.p1.y, bbox.p2.y, viospace, viowidth)
    #
    #     # Retrieve the recursive
    #     shapeit = cell.begin_shapes_rec(layer)
    #     shapeit.shape_flags = pya.Shapes.SPolygons | pya.Shapes.SBoxes
    #
    #     # feed the data into the cleaner
    #     reg = pya.Region(shapeit)
    #     reg.merge()
    #     for poly in reg.each_merged():
    #         for edge in poly.each_edge():
    #             sl.add_data(edge.x1, edge.x2, edge.y1, edge.y2)
    #     # Sort the edges in an ascending order. Also, removes touching edges or edges within other shapes.
    #     sl.sort()
    #     if viowidth != 1 and viospace != 1:
    #         sl.clean()
    #     # Create a region from the cleaned data. This is a bit slow. There might be a way to do it faster. The
    #     # Region merge seems to be the most time consuming process.
    #     region_cleaned = pya.Region()
    #     for row in range(bbox.p1.y, bbox.p2.y):
    #         r = sl.get_row(row)
    #         if r.size:
    #             y1 = row
    #             y2 = row + 1
    #             for x1, x2 in zip(r[::2], r[1::2]):
    #                 region_cleaned.insert(pya.Box(int(x1), int(y1), int(x2), int(y2)))
    #     region_cleaned.merge()
    #
    #     # Clean the target layer and fill in the cleaned data
    #     cell.clear(layer)
    #     cell.shapes(layer).insert(region_cleaned)
    #     if qtprogress:
    #         progress.inc()
    progress._destroy()
