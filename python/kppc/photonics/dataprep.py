# This file is part of KLayoutPhotonicPCells, an extension for Photonic Layouts in KLayout.
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

import pya
import kppc


def file_len(fname: str):
    """Returns the number of lines in the file fname"""
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def add(layout, cell, slayers, dlayers, ex_amount, layers, out_cell=None):
    """Combines all slayers' shapes into a region and merges this region with each of dlayers' regions.

    :param layout: the layout on which the cells are located
    :param cell: the cell from which to copy the layers (source shapes)
    :param slayers: the layers to copy
    :param dlayers: the layers where to copy to
    :param ex_amount: the amount added around the source shapes
    :param layers: the layermapping
    :param out_cell: the cell where to put the shapes. If not specified, the input cell will be used.
    """
    # adjust amount from microns to database units
    am = ex_amount / layout.dbu

    if out_cell:
        o_cell = out_cell
    else:
        o_cell = cell

    srclayers = [slayers, ] if isinstance(slayers, str) else slayers
    dstlayers = [dlayers, ] if isinstance(dlayers, str) else dlayers

    in_layers = [layout.layer(layers[m][0], layers[m][1]) for m in srclayers]
    region = pya.Region()
    for layer in in_layers:
        if layer != -1:
            shapeit = cell.begin_shapes_rec(layer)
            region.insert(shapeit)
    region.merge()
    if ex_amount > 0:
        # increase the size of the region
        region.size(am)
        region.merge()
    for layer in dstlayers:
        layer_n, layer_d = layers[layer]
        l = layout.layer(layer_n, layer_d)
        shapeit = o_cell.begin_shapes_rec(l)
        add_region = pya.Region()
        add_region.insert(shapeit)
        add_region.merge()
        o_cell.shapes(l).clear()
        o_cell.shapes(l).insert(add_region + region)


def sub(layout, cell, slayers, dlayers, ex_amount, layers, out_cell=None):
    """Analogous to :func:`~kppc.photonics.dataprep.add`

    Instead of perfoming a combination with the destination layers, this function will substract the input region.
    """
    if out_cell:
        o_cell = out_cell
    else:
        o_cell = cell

    am = ex_amount / layout.dbu

    srclayers = [slayers, ] if isinstance(slayers, str) else slayers
    dstlayers = [dlayers, ] if isinstance(dlayers, str) else dlayers

    in_layers = [layout.layer(layers[m][0], layers[m][1]) for m in srclayers]
    region = pya.Region()
    for layer in in_layers:
        if layer != -1:
            shapeit = layout.begin_shapes(cell, layer)
            region.insert(shapeit)
    region.merge()
    if ex_amount != 0:
        region.size(am)
        region.merge()
    for layer in dstlayers:
        sub_region = pya.Region()
        layer_n, layer_d = layers[layer]
        l = layout.layer(layer_n, layer_d)
        shapeit = o_cell.begin_shapes_rec(l)
        sub_region.insert(shapeit)
        sub_region.merge()
        o_cell.shapes(l).clear()
        o_cell.shapes(l).insert(sub_region - region)


def dataprep(in_cell, layout, out_cell=None, config=None, layers_org=None):
    """Dataprep that creates excludes layers etc. with boolean operation on input layers that will be added/substracted to outputlayers.

    :param in_cell: the cell from which to take shapes
    :param layout: the layout on which we perform the operations (most likely self.layout)
    :param out_cell: the output cell. if not specified take the input cell
    :param config: the config file. This file specifies the boolean operations (self.dataprepconfig)
    :param layers_org: the original layermap we use (most likely self.layermap)
    """
    # without config or layermap we can't work
    if config is None:
        return
    if layers_org is None:
        return
    layers = {}

    if kppc.settings.General.Progressbar:
        l = file_len(config)
        progress = pya.RelativeProgress('Layermapping from abstract to Foundry Layers', l)

    # create one dimensional dictionary of the layermap (maybe remove in the future as this is not necessary anymore
    for key in layers_org:
        for k in layers_org[key]:
            layers[key + '.' + k] = [int(i) for i in layers_org[key][k]]

    # define conveniance functions
    def _add(slayers, dlayers, amount=0, layers=layers):
        add(layout, in_cell, slayers, dlayers, amount, layers, out_cell)

    def _sub(slayers, dlayers, amount=0, layers=layers):
        sub(layout, in_cell, slayers, dlayers, amount, layers, out_cell)

    count = 0

    # process the config file
    with open(config, 'r') as df:
        for line in df:
            strings = line.split()

            if strings[0] == 'add':
                if len(strings) == 4:
                    amount = float(strings[3])
                else:
                    amount = 0
                progress.format = 'Adding Layer(s) {} to Layer {}'.format(strings[1].split(','),
                                                                                 strings[2].split(','))
                _add(strings[1].split(','), strings[2].split(','), amount)
                progress.inc()
            elif strings[0] == 'sub':
                if len(strings) == 4:
                    amount = float(strings[3])
                else:
                    amount = 0
                progress.format = 'Subtracting Layer(s) {} from Layer {}'.format(strings[1].split(','),
                                                                              strings[2].split(','))
                _sub(strings[1].split(','), strings[2].split(','), amount)
                progress.inc()
            else:
                progress.inc()
    progress._destroy()
