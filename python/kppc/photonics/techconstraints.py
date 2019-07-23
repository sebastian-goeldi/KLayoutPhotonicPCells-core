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

# Simple function to read the minWidth/minSpacings from the techfile

import re
import os


def load_from_tech(techfile: str):
    
    read = False
    
    tech = {}
    
    with open(techfile, 'r') as thefile:
        for i, line in enumerate(thefile):
            if ';spacings' in line:
                read = False
                continue
            if 'spacings' in line:
                read = True
                continue
            if ';orderedSpacings' in line:
                read = False
                continue
            if 'orderedSpacings' in line:
                read = True
                continue
            
            if read:
                l = line.strip()
                lyst = l.split()
                for key in lyst[2:-2]:
                    k = key.strip('"')
                    if k not in tech:
                        tech[k] = {}
                    tech[k][lyst[1]]=float(lyst[-2])
    return tech