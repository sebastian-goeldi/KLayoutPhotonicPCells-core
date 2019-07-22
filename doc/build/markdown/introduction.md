# Introduction

The KLayoutPhotonicPCells\`kppc\` module is an extension for KLayout PCells to facilitate photonic PCells.
Photonics often works with the concept of ports.
Ports are defined by a coordinate and a direction. In the case of this module ports will be stored in PCell parameters in the background.
They are serialized [KLayout Trans](https://www.klayout.de/doc/code/class_ICplxTrans.html) objects. For an introduction on how to build your own PCell Library, have a look at
how to create Example Library.

When building PCell Libraries it is recommended to build it with three packages as shown in
