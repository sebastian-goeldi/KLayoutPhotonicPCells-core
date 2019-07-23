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


def load(filename: 'str'):
    """
    Simple routine to read a .layermap file into a dictionary

    :param filename: Filename with path
    :type filename: str
    :return: Dictionary of dictionaries in the form of {layer: {purpose1:(layer_number,purpose_number),
        purpose2:(layer_number1,purpose_number2)},layer2: {...} }
    :rtype: dict

    :Examples:
        >>> import kppc.photonics.layermaps as lm
        >>> lm.load(os.path.expanduser('~/.klayout/salt/zccmos/FreePDK45_tech/tech/FreePDK45.layermap'))
        {'pwell': {'blockage': ('109', '1'), 'drawing': ('109', '0')}, ... }
    """
    if filename.split('.')[-1] != 'layermap':
        filename += '.layermap'
    layers = {}

    with open(filename, 'r') as thefile:
        for line in thefile:
            strings = line.split()
            if strings[0][0] == ';':
                continue
            else:
                if strings[0] in layers:
                    layers[strings[0]][strings[1]] = (int(strings[2]), int(strings[3]))
                else:
                    layers[strings[0]] = {strings[1]: (int(strings[2]), int(strings[3]))}
    return layers
