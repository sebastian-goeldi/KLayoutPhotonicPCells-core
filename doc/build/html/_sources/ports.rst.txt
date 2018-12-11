Ports
=====

Ports are a concept used in photonics. They are very similar to pins in electronics, as they both describe connections
between cells. The big difference between ports and pins is ports have additional properties that are important
for photonics. When connecting photonic devices it is necessary that the device connections are aligned. For example, if
two waveguides are connected, the connected endings have to point on the opposite direction and the connections have to
be the same size.

This module implements the concept of ports into KLayout PCells. Currently ports track location, orientation and length.
If two ports have a mismatch in width, they cannot be connected. New ports can be created in PCells with the
:class:`kppc.photonics.PortCreation` when overriding the :meth:`kppc.photonics.PhotDevice.create_param_inst` method
in the PCell Library. If any instantiated child cells in a PCell have any open ports (not connected to another port of another
child cell), they are passed upwards to the cell itself and are announced as ports of this cell.
This hierarchical design allows to create arbitrary Devices independent of the order when assembling them.

.. note:: Make sure ports are drawn correctly. If texts in ports aren't oriented alond the width of the port, set the boolean
    `Transform text with cell instance` in :menuselection:`File --> Setup --> Display --> Cells` to true
    and make sure the text font is not set to the default font.
