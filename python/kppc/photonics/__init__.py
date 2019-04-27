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

"""Photonic PCell-Extension Module

.. warning ::
    Before using this module for the first time, make sure the `kppc.drc.slcleaner`
    submodule is compiled and importable, as this  module relies on the drc package for DR-Cleaning. See :py:mod:`drc`
    for further details.

A Module which provides extensions for standard KLyaout-PCells. This extension mainly provides functionalities for
photonics. One main feature of photonics are so-called ports. These define a position and a direction on a Cell.
They indicate where multiple Cells/Devices should interact with each other. For example, one can connect a waveguide
with a linear taper. This module provides the classes and functions for this functionality. Additionally, this module
provides a lot of convenience functions for interactions with the KLayout-API.

The main functionality for this module is in the class :class:`~kppc.photonics.PhotDevice`.

.. warning ::  When using this module to extend a PCell-Library any PCell class has to assign valid values to the
    parameters ``layermap`` , ``dataprep_config`` , ``clean_rules`` . These are accessed by :py:class:`~kppc.photonics.
    PhotDevice`. If they aren't declared, a runtime error will occur.

"""

# make sure the setup script is compiled

import pya
import kppc.drc
from collections import namedtuple
import kppc.photonics.dataprep
from time import clock

# Namedtuple to hold position of a port.
PortCreation = namedtuple('PortCreation', ['x', 'y', 'rot', 'length'])
"""Custom namedtuple

This will hold informations for creating ports.

:param x: x Coordinate [microns]
:type x: int
:param y: y Coordinate [microns]
:type y: int
:param rot: Rotation in degrees
:type int: int
:param length: Port length [microns]
:type length: float
"""


def isnamedtupleinstance(x):
    """Test if something is a named tuple
    This allows to test if `x` is a port (PortCreation object) or just a list of instance descriptions
    """
    typ = type(x)
    base = typ.__bases__
    if len(base) != 1 or base[0] != tuple:
        return False
    fields = getattr(typ, '_fields', None)
    if not isinstance(fields, tuple):
        return False
    return all(type(n) == str for n in fields)


class InstanceHolder:
    """Class to keep track and hold the information of a pcell instance. The information will be processed to a PCell in
     :func:`~kppc.photonics.PhotDevice.produce_impl`
    """

    def __init__(self, cell_name, lib, pcell_decl, params=None, params_mod=None, id=0):
        """
        Initialize the class

        :param cell_name: The name of the cell which will be instantiated
        :param lib: Library from which the cell will be instantiated
        :param pcell_decl: the pya.PCellDeclaration object reference
        :param params: The unmodified parameters of the object
        :param params_mod: The coerced parameter set
        :param id: id of the object. Ids determine the order in which the instances are created
        """
        self.id = id
        self.params = params
        self.params_mod = params_mod
        self.movement = None
        self.connection = None
        self.connection_port = None
        self.port_to_connect = None
        self.cell_name = cell_name
        self.lib = lib
        self.pcell_decl = pcell_decl
        self.placed = False

    def port_to_port(self, port: int, inst_holder: tuple):
        """Attach one of this instance's ports to another instance's port.

        :param port: port of this instance
        :param inst_holder: Tuple of the the reference to the other instance and the port to connect to.
            This is a tuple returned from <InstanceHolder object>.port(<portnumber>).
        """
        if self.movement:
            raise ValueError('Cannot move an instance and connect to a port as these operations are mutually exlusive')
        self.connection = inst_holder[0]
        self.connection_port = inst_holder[1]
        self.port_to_connect = port

    def port(self, port: int):
        """
        Returns a reference to itself and the port number. No checks are made whether this port is valid or not!
        Available ports can be seen if such an object is instantiated.

        :param port: index of the port
        :return: self, port
        """
        return self, port

    def move(self, x: float = 0, y: float = 0, rot: int = 0, mirrx: bool = False, mag: float = 1):
        """Moves an instance. Units of microns relative to origin.

        :param x: x position where to move
        :type x: float
        :param y: y position where to move
        :type y: float
        :param rot: Rotation of the object in degrees
        :type rot: int
        :param mirrx: Mirror at x-axis if True
        :type mirrx: bool
        :param mag: Magnification of the Cell. This feature is not tested well.
        :type mag: float
        """
        if self.connection:
            raise ValueError(
                'Cannot connect to a port of another instance and move the same instance. These operations are '
                'mutually exlusive')
        self.movement = pya.DCplxTrans(mag, rot, mirrx, x, y)


class PhotDevice(pya.PCellDeclarationHelper):
    """Wrapper for calls to the Klayout API.

    :ivar dict layermap: The layermap dictionary. This value has to be written by a child class. If undefined this
        class won't work and crash.
    :ivar str dataprep_config: String with the path to the file containing the dataprep instructions.
        If left empty, dataprep will do nothing.
    :ivar list clean_rules: String with the path to the file containing the DR-Cleaning rules.
        If left empty, DR-Cleaning will do nothing. If the cells are built similar to the FreePDK45-SampleCells example,
        DR-Cleaning will not work without dataprep, or will be without any effect.
    :ivar bool keep: Parameter created during :func:`__init__` via pya.DeclarationHelper. If set to True in the PCell,
        all child-cells will be preserved at the end. If set to False only the Dataprep Sub-Cell will be preserved.
    :ivar bool dataprep: If this flag is set, :func:`kppc.photonics.dataprep.dataprep` will be performed on the cell.
        The variable :attr:`dataprep_config` holds the path to the instructions for dataprep.
    :ivar bool clean: If this flag is set, :func:`kppc.drc.clean` will be performed on the cell.
        Rules for the DR-Cleaning are pulled from :attr:`clean_rules`.
    :ivar bool top: Hidden parameter that indicates whether this cell is a top_cell. Default is yes. When an instance is
        added through :meth:`.add_pcell_variant` these cells will not be set to top_cells as they are instantiated from
        another cell.
    :ivar only_top_ports: GUI parameter. If set to true, only ports of the top most hierarchy level (top_cell) will be
        annotated by text.
    """

    def __init__(self):
        """
        Initialization of the class. This will add automatically several PCell parameters to the class as documented in
        the class.
        """
        pya.PCellDeclarationHelper.__init__(self)
        self.param("portlist", self.TypeString, "Portlist", hidden=True, default="", readonly=True)
        self.param("transformations", self.TypeString, "Child PCell Transformations", hidden=True, default="",
                   readonly=True)
        # Disable the option to flatten cell for the moment
        self.param("keep", self.TypeBoolean, "Keep original Cell?", hidden=True, default=True, readonly=True)
        self.param('dataprep', self.TypeBoolean, "Data Prep?", hidden=False, default=False, readonly=False)
        self.param('drc_clean', self.TypeBoolean, 'Clean DRC violations?', hidden=False, default=False,
                   readonly=False)
        self.param('top', self.TypeBoolean, 'Is top cell?', hidden=True, default=True, readonly=True)
        self.param('only_top_ports', self.TypeBoolean, 'Show only Ports of Top Cell?', hidden=False, default=True,
                   readonly=False)

        self.layermap = None
        self.dataprep_config = None
        self.clean_rules = None

        self.transformations = ''
        self.portlist = ''

    def get_layer(self, name: str, purpose: str = ''):
        """Creates LayerInfo object

        Creates a pya.LayerInfo object to find layer indexes in the current layout.

        :param name: name of the layer
        :param purpose: if not empty then layer and purpose are separate
        :return: pya.LayerInfo about the layer
        """
        if purpose:
            layer = self.layermap[name][purpose]
        else:
            layer = self.layermap[name.split('.')[0]][name.split('.')[1]]
        return pya.LayerInfo(int(layer[0]), int(layer[1]), name)

    @staticmethod
    def connect_port_to_port(port1: tuple, port2: tuple):
        """ Connect Ports from two InstanceHolder instances.

        Connect two `InstanceHolders` together. Attach <InstanceHolder instance1>.port(<port1>) to
        <InstanceHolder instance2>.port(<port2>). This will apply a transformation to Instance2.
        There can only be either a transformation through connect_port_to_port or through InstanceHolder.move

        :param port1: <InstanceHolder instance1>.port(<port1>)
        :param port2: <InstanceHolder instance2>.port(<port2>)
        """
        port2[0].port_to_port(port2[1], port1)

    @staticmethod
    def flip_shape_xaxis(shape: 'pya.Shape'):
        """Flip a polygon (or any shape) at the x-axis

        :param shape: pya.Shape object (e.g. through photonicpcell.create_polygon obtained)
        """
        shape.transform(pya.ICplxTrans.M0)

    @staticmethod
    def flip_shape_yaxis(shape: 'pya.Shape'):
        """Flip a polygon (or any shape) at the y-axis

        :param shape: pya.Shape object (e.g. through photonicpcell.create_polygon obtained)
        """
        shape.transform(pya.ICplxTrans.M90)

    def create_port(self, x: float, y: float, rot: int = 0, length: int = 0):
        """Creates a Port at the specified coordinates.

        This function will be used when a port is created through the PortCreation tuple.

        :param x: x Coordinate in microns
        :param y: y Coordinate in microns
        :param rot: Rotation in degrees
        :param length: length of the port in microns
        """
        # Append a serialized transformation to the code.
        if self.portlist != "":
            self.portlist += ";"
        trans = pya.CplxTrans(1, rot, False, x / self.layout.dbu, y / self.layout.dbu)
        self.portlist += trans.to_s()
        self.portlist += ":"
        self.portlist += str(int(length / self.layout.dbu))

    def clear_ports(self):
        """Clears self.portlist and by that delete all ports. This is used when updating the Ports
        """
        # Delete all ports in the string
        self.portlist = ""

    def connect_port(self, pos1: int, portlist1: str, port1: int, pos2: int, portlist2: str, port2: int) -> int:
        """ Connect ports of two instances. The second instance will be transformed to attach to the first instance.

        :param pos1: index of instance1
        :param portlist1: portlist of instance1
        :param port1: port number of instance1
        :param pos2: index of instance2
        :param portlist2: portlist of instance2
        :param port2: port number of instance2
        """
        p1, l1 = portlist1.split(';')[port1].split(':')
        p2, l2 = portlist2.split(';')[port2].split(':')

        if l1 != l2:
            return -1

        child_trans = self.transformations.split(';')

        trans1 = pya.ICplxTrans.from_s(child_trans[pos1]) * pya.ICplxTrans.from_s(p1)

        if trans1.is_mirror():
            trans1.mirror = False

        trans2 = pya.ICplxTrans.R180 * pya.ICplxTrans.from_s(p2).inverted()

        child_trans[pos2] = pya.ICplxTrans.to_s(trans1 * trans2)
        transformation = ''
        for i, string in enumerate(child_trans):
            transformation += string
            if i != len(child_trans) - 1:
                transformation += ';'
        self.transformations = transformation
        return 0

    def create_polygon(self, points: 'list or pya.DPolygon', layer: int):
        """Creates a Polygon and adjusts from microns to database units. Format: [[x1,y1],[x2,y2],...] in microns

        :param points: Points defining the corners of the polygon.
        :param layer: layer_index of the target layer
        :return: reference to polygon object
        """
        if isinstance(points, pya.DPolygon) or isinstance(points, pya.Polygon):
            self.cell.shapes(self.layout.find_layer(layer)).insert(points)
        else:
            pts = []
            for p in points:
                pts.append(pya.DPoint(p[0], p[1]))
            return self.cell.shapes(self.layout.find_layer(layer)).insert(pya.DPolygon(pts))

    def create_path(self, points: list, width: float, layer: 'pya.LayerInfo'):
        """Creates a pya.Path object and inserts it into the Library-PCell.

        :param points: The points describing the path [[x1,y1],[x2,y2],...] in microns
        :param width: Path width
        :param layer: layer on which the path should be made
        """
        pts = []
        for p in points:
            pts.append(pya.Point(pya.DPoint(p[0] / self.layout.dbu, p[1] / self.layout.dbu)))
        w = int(width / self.layout.dbu)
        self.cell.shapes(self.layout.find_layer(layer)).insert(pya.Path(pts, w))

    def insert_shape(self, shape: pya.Shape, layer: 'pya.LayerInfo'):
        """Any other Klayout shape can be added to the PCell through this function.

        :param shape: pya.Shape object
        :param layer: layer where to write to
        :return: reference to shape
        """
        return self.cell.shapes(self.layout.find_layer(layer)).insert(shape)

    def add_layer(self, var_name: str, name: str = '', ld=tuple(),
                  field_name: str = '',
                  hidden=False):
        """Add a layer to the layer list of the pcell by name.

        :param var_name: name of the variable
        :param name: name in the pcell window
        :param ld: layer,dataype touple
        :param field_name:
        :param hidden: hide in the GUI

        :Examples:
            self.add_layer('lpp','rx1phot.drawing')
        """
        if name:
            linfo = self.get_layer(name)  # self.layermap[ln][dn]
        elif ld:
            layer, datatype = ld
            linfo = pya.LayerInfo(layer, datatype)
        else:
            raise AttributeError("Either Name or Layer/Dataype touple necessary")

        self.param(var_name, self.TypeLayer, field_name, hidden=hidden, default=linfo)

    def add_params(self, params: dict):
        """Create the PCell conform dictionary from a parameter list

        :param params: Dictionary of parameters
        """
        for key in sorted(params):
            if '_choices' in key:
                continue
            df = params[key]
            if type(df) == float:
                t = self.TypeDouble
            elif type(df) == int:
                t = self.TypeInt
            elif type(df) == bool:
                t = self.TypeBoolean
            elif type(df) == list:
                t = self.TypeList
            elif type(df) == str:
                t = self.TypeString
            elif type(df) == pya.Shape:
                t = self.TypeShape
            elif type(df) is None:
                t = self.TypeNone
            if key + '_choices' in params:
                self.param(key, t, key, default=params[key], choices=params[key + '_choices'])
            else:
                self.param(key, t, key, default=params[key])

    @staticmethod
    def decl(libname: str, cellname: str):
        """Get pya.PCellDeclaration of a cell in a library

        :param libname: Name of the library
        :param cellname: Name of the cell
        :return: pya.PCellDeclaration reference of PCell
        """
        lib = pya.Library.library_by_name(libname)
        if not lib:
            raise Exception("Unknown lib '{}'".format(libname))

        pcell_decl = lib.layout().pcell_declaration(cellname)
        if not pcell_decl:
            raise Exception("Unkown PCell '{}'".format(cellname))
        return pcell_decl

    def update_parameter_list(self, params: dict, decl: 'pya.PCellDeclaration'):
        """Coerces parameter list. This is necessary to calculate port locations and update parameters in general.

        :param params: dict of parameters
        :param decl: pya.PCellDeclaration reference
        :return: list of updated parameters
        """
        param_list = [params.get(p.name, p.default) for p in decl.get_parameters()]
        param_list = decl.coerce_parameters(self.layout, param_list)
        return param_list

    def calculate_ports(self, instances: list):
        """Calculates port locations in the cell layout. This is to propagate the port locations upwards

        :param instances: list containing :class:`kppc.photonics.InstanceHolder`
        """
        porttrans = []
        if self.transformations != '':
            # Check child cells ports. If there are ports which are not populated by other ports, add them as own ports
            trans = [pya.ICplxTrans.from_s(i) for i in self.transformations.split(';')]
            for i, inst in enumerate(instances):
                if not inst.params_mod[0]:
                    continue
                ports = [pya.ICplxTrans.from_s(k.split(':')[0]) for k in inst.params_mod[0].split(';')]
                lengths = [k.split(':')[1] for k in inst.params_mod[0].split(';')]
                for q, r in zip(ports, lengths):
                    porttrans.append([trans[i] * q, r])
        if self.portlist != '':
            # Add manually created Ports
            porttrans.extend(
                [[pya.ICplxTrans.from_s(p.split(':')[0]), p.split(':')[1]] for p in self.portlist.split(';')])

        porttrans = sorted(porttrans, key=lambda x: (x[0].disp.x, x[0].disp.y))
        # Add the calculated ports as own ports
        self.portlist = ''
        m180 = pya.ICplxTrans(1, 180, True, 0, 0)
        for p in porttrans:
            if not ([p[0] * pya.ICplxTrans.R180, p[1]] in porttrans or [p[0] * m180, p[1]] in porttrans):
                if self.portlist != '':
                    self.portlist += ';'
                self.portlist += str(p[0]) + ':' + p[1]

    def get_transformations(self):
        """Convert transformation strings back to pya.ICplxTrans objects

        :return: list of pya.ICplxTrans objects
        """
        return [pya.ICplxTrans.from_s(i) for i in self.transformations.split(';')]

    def set_transformation(self, ind: int, trans: 'pya.ICplxTrans'):
        """Transforms child cells to the intended position, defined either by connected ports or by manual
        positioning.

        :param ind: index of the child cell
        :param trans: Transformation object with which to transform the child cell
        """
        trans_list = self.get_transformations()
        trans_list[ind] = trans
        self.transformations = ''
        for i, t in enumerate(trans_list):
            if i > 0:
                self.transformations += ';'
            self.transformations += t.to_s()

    def add_pcell_variant(self, params: dict, number: int = 1):
        """Add variants of PCells. Creates a list of InstanceHolders and modifies their parameters accordingly.

        :param params: parameter list from which to create pcells
        :param number: Number of instances to create
        :return: list of :class:`kppc.photonics.InstanceHolder`
        """
        params_copy = params.copy()
        cellname = params_copy.pop('cellname')
        libname = params_copy.pop('lib')
        params_copy['top'] = False
        params_copy['only_top_ports'] = self.only_top_ports
        pcell_decl = self.decl(libname, cellname)
        params_mod = self.update_parameter_list(params_copy, pcell_decl)
        instance_list = []

        for i in range(number):
            instance_list.append(
                InstanceHolder(cellname, libname, pcell_decl, params=params, params_mod=params_mod, id=i))
        if number == 1:
            return instance_list[0]
        else:
            return instance_list

    def add_pcells(self, instance_list: list):
        """Creates list of instances of PCells. These are the effective Klayout cell instances.
        
        :param instance_list: list of :class:`kppc.photonics.InstanceHolder`
        :return: list of instantiated pya.CellInstArray
        """
        uid = 0
        insts = []
        for inst_port in instance_list:
            if type(inst_port) is InstanceHolder:
                inst_port.id = uid
                uid += 1
                insts.append(inst_port)
            elif type(inst_port) is list:
                for iinst_port in inst_port:
                    if type(iinst_port) is InstanceHolder:
                        iinst_port.id = uid
                        uid += 1
                        insts.append(iinst_port)
            else:
                raise ValueError(
                    "Expected type instances (InstanceHolder), ports (PortCreation) or a list of instances,"
                    "ports. Instead got {}".format(str(type(inst_port))))

        trans = self.get_transformations()
        instances = []
        for i, inst in enumerate(insts):
            pcell_var = self.layout.add_pcell_variant(inst.pcell_decl.id(), inst.params_mod)
            instances.append(self.cell.insert(pya.CellInstArray(pcell_var, trans[i])))
        return instances

    def move_instance(self, ind: int, trans: 'pya.ICplxTrans', mirror: bool = False):
        """Moves an InstanceHolder object

        :param ind: id of the InstanceHolder
        :param trans: list of transformations
        :param mirror: bool whether to mirror the object
        """
        trans = pya.ICplxTrans(1, trans[2], mirror, trans[0], trans[1])
        self.add_transformation(trans, ind)

    def coerce_parameters_impl(self):
        """Method called by Klayout to update a PCell. For photonic PCells the ports are updated/calculated in the
        parameter of the PCell. And desired movement transformations are performed.

        Because the calculated ports of our own PCell are used by parent cells and are needed before
        `~produce_impl`, we must calculate them twice. First to calculate where our own ports are and then again to
        instantiate the child cells. This is unfortunate but not a big problem, since dataprep and DR-cleaning take
        the majority of computation time.

        :return:
        """
        self.clear_ports()
        instances_and_ports = self.create_param_inst()
        if not instances_and_ports:
            return
        if isnamedtupleinstance(instances_and_ports) or isinstance(instances_and_ports, InstanceHolder):
            instances_and_ports = [instances_and_ports]
        id = 0
        insts = []
        for inst_port in instances_and_ports:
            # For each object test if it is a list of InstanceHolders/Port or plain objects and then separate them
            # accordingly
            if isinstance(inst_port, InstanceHolder):
                inst_port.id = id
                id += 1
                insts.append(inst_port)
            elif isnamedtupleinstance(inst_port):
                self.create_port(inst_port.x, inst_port.y, inst_port.rot, inst_port.length)
            elif type(inst_port) is list:
                for iinst_port in inst_port:
                    if isinstance(iinst_port, InstanceHolder):
                        iinst_port.id = id
                        id += 1
                        insts.append(iinst_port)
                    elif isnamedtupleinstance(iinst_port):
                        self.create_port(iinst_port.x, iinst_port.y, iinst_port.rot, iinst_port.length)
            else:
                raise ValueError(
                    "Expected type instances (InstanceHolder), ports (PortCreation) or a list of instances,"
                    "ports. Instead got {}".format(str(type(inst_port))))
        self.transformations = ''
        # If child instances have requested movements in their InstanceHolder move them now
        for i, inst in enumerate(insts):
            if self.transformations:
                self.transformations += ';'
            if inst.movement:
                # Adjust movement for database
                inst.movement.disp = pya.Vector(inst.movement.disp.x / self.layout.dbu,
                                                inst.movement.disp.y / self.layout.dbu)
                self.transformations += inst.movement.to_s()
                inst.placed = True
            elif inst.connection:
                self.transformations += pya.ICplxTrans.R0.to_s()
            else:
                self.transformations += pya.ICplxTrans.R0.to_s()
                inst.placed = True
        # If the InstanceHolder object has a Port to connect to, calculate the transformation
        all_placed = False
        count = 0
        while (not all_placed) and count < 50:
            all_placed = True
            count += 1
            for i, inst in enumerate(insts):
                if inst.connection:
                    if not inst.connection.placed:
                        all_placed = False
                        continue
                    retcode = self.connect_port(inst.connection.id, inst.connection.params_mod[0], inst.connection_port,
                                                inst.id,
                                                inst.params_mod[0], inst.port_to_connect)
                    if retcode < 0:
                        msg = pya.QMessageBox(pya.Application.instance().main_window())
                        msg.text = 'Port {} of {} cannot be connected to Port {} of {}'.format(inst.port_to_connect,
                                                                                               inst.connection.params[
                                                                                                   'cellname'],
                                                                                               inst.port_to_connect,
                                                                                               inst.params['cellname'])
                        msg.windowTitle = 'ImportError'
                        msg.exec_()
                        return False
                    inst.placed = True
        # Update the transformations and self.portlist with the calculated transformations of the children
        self.calculate_ports(insts)

    def produce_impl(self):
        """Create the effective Klayout shapes. For this all the InstanceHolders are cycled through and all the child
        instances are created. Furthermore, if desired, dataprep is performed, which copies and sizes the shapes as
        desired. Dataprep will only create shapes on the topmost cell. Finally, if desired DR-cleaning is performed and
        in the process the shapes will be manhattanized.
        """

        if self.layermap is None:
            raise NotImplementedError(
                'self.layermap has to be defined by the PCell. You can either do this in the PCell initialization or '
                'in a Class that all PCells inherit from. See the documentation for more details')
        if self.dataprep_config is None:
            raise NotImplementedError(
                'self.dataprep_config has to be defined by the PCell. You can either do this in the PCell '
                'initialization or in a Class that all PCells inherit from. See the documentation for more details')
        if self.clean_rules is None:
            raise NotImplementedError(
                'self.clean_rules has to be defined by the PCell. You can either do this in the PCell initialization '
                'or in a Class that all PCells inherit from. See the documentation for more details')
        instances_and_ports = self.create_param_inst()
        uid = 0
        insts = []

        # Because we cannot safe anything between coerce_parameters and here, we must calculate this again.
        if isnamedtupleinstance(instances_and_ports) or isinstance(instances_and_ports, InstanceHolder):
            instances_and_ports = [instances_and_ports]
        for inst_port in instances_and_ports:
            if isinstance(inst_port, InstanceHolder):
                inst_port.id = uid
                uid += 1
                insts.append(inst_port)
            elif isnamedtupleinstance(inst_port):
                continue
            elif isinstance(inst_port, list):
                for iinst_port in inst_port:
                    if isinstance(iinst_port, InstanceHolder):
                        iinst_port.id = uid
                        uid += 1
                        insts.append(iinst_port)
                    elif isnamedtupleinstance(iinst_port):
                        continue
            else:
                raise ValueError(
                    "Expected type instances (InstanceHolder), ports (PortCreation) or a list of instances,"
                    "ports. Instead got {}".format(str(type(inst_port))))
        # If we have child cells to create, create them now
        if insts:
            self.add_pcells(insts)
        # Create the shapes created in this PCell
        self.shapes()

        if self.top or not self.only_top_ports:
            # If this is a top cell or we want to draw all ports, draw the texts.
            # To make sure that texts of ports get drawn correctly set the boolean
            # to true in File-> Setup -> Display -> Settings -> Cells -> 'Transform text with cell instance'
            # and make sure it's not set to Default font

            if self.portlist:
                for i, p in enumerate(self.portlist.split(';')):
                    trans = pya.ICplxTrans.from_s(p.split(':')[0]).s_trans()

                    trans.rot = (trans.rot + 1 % 4)
                    if trans.is_mirror():
                        trans.rot = (trans.rot + 2 % 4)

                    valign = halign = 1

                    if trans.rot % 2:
                        valign = 2
                    else:
                        halign = 2

                    text = pya.Text("Port {}".format(i), trans)

                    text.halign = halign
                    text.valign = valign

                    self.cell.shapes(self._layers[0]).insert(text)
            # For the dataprep, do we want to keep the original shapes and child-cells?
        cl1 = clock()

        if self.keep:
            # Yes, so we create a new child cell called 'DataPrep' to create the dataprep shapes in
            if self.dataprep:
                prep_cell = self.layout.create_cell('DataPrep')
                prep_cell._create()
                kppc.photonics.dataprep.dataprep(self.cell, self.layout, prep_cell, config=self.dataprep_config,
                                                 layers_org=self.layermap)
                self.cell.insert(pya.CellInstArray(prep_cell.cell_index(), pya.Trans.R0))
                if self.drc_clean:
                    rules = self.clean_rules
                    # Convert Micrometers to database units
                    for cr in rules:
                        cr[1] = int(cr[1] / self.layout.dbu)
                        cr[2] = int(cr[2] / self.layout.dbu)
                    kppc.drc.clean(prep_cell, rules)

        else:
            # the dataprep will clean all children and shapes and then insert cleaned ones
            if self.dataprep:
                temp_cell = self.layout.create_cell('DataPrep_del')
                temp_cell._create()
                kppc.photonics.dataprep.dataprep(self.cell, self.layout, temp_cell, config=self.dataprep_config,
                                                 layers_org=self.layermap)

                if self.drc_clean:
                    rules = self.clean_rules
                    # Convert Micrometers to database units
                    for cr in rules:
                        cr[1] = int(cr[1] / self.layout.dbu)
                        cr[2] = int(cr[2] / self.layout.dbu)
                    kppc.drc.clean(temp_cell, rules)
                # Delete all child cells
                self.cell.clear()
                self.cell.insert(pya.CellInstArray(temp_cell.cell_index(), pya.Trans.R0))
                self.cell.flatten(True)

        print('Time for dataprep and DR-cleaning:')
        print(clock() - cl1)

    def create_param_inst(self):
        """To be overwritten by the effective PCell

        :return: Iterable with the declarations of the child PCells.
        """
        return []

    def shapes(self):
        """To be overwritten by effective PCell if shapes should be desired.

        :rtype: None
        """
        return
