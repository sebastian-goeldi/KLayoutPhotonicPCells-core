# Technology Import

To use KLayout and the Photonics-extension efficiently, it is recommended to create a KLayout technology. This chapter explains how to import a technology.

To use a new technology either create a new technology from the technology manager Tools ‣ Manage Technologies or create a new package
Tools ‣ Manage Packages for the technology.

## Import Techfile & Creation of LayerProperties

KLayout provides an import script for Cadence techfiles. This import creats the Layer Properties automatically for the defined layers.

The script can be found in File ‣ Import Cadence Techfile

After importing, the properties can be saved via File ‣ Save Layer Properties. Recommended location for the file is in the technology folder in ~/.klayout/tech/<technology-name>/<file> or if using a package
~/.klayout/salt/<technology-package>/tech/<filename>

**NOTE**: Suggested filename for easy use with the sample cells: FreePDK45.tf / FreePDK45.lyp

In order to use the additional abstract layers in the sample cells paste the following xml snippets into the <>.lyp file:

```
<properties>
    <frame-color>#01ff6b</frame-color>
    <fill-color>#01ff6b</fill-color>
    <frame-brightness>0</frame-brightness>
    <fill-brightness>0</fill-brightness>
    <dither-pattern>I3</dither-pattern>
    <line-style>I6</line-style>
    <valid>true</valid>
    <visible>true</visible>
    <transparent>false</transparent>
    <width>1</width>
    <marked>false</marked>
    <xfill>false</xfill>
    <animation>0</animation>
    <name>phot_silicon.drawing</name>
    <source>400/0@1</source>
</properties>
<properties>
    <frame-color>#808080</frame-color>
    <fill-color>#808080</fill-color>
    <frame-brightness>0</frame-brightness>
    <fill-brightness>0</fill-brightness>
    <dither-pattern>I2</dither-pattern>
    <line-style>I0</line-style>
    <valid>true</valid>
    <visible>true</visible>
    <transparent>false</transparent>
    <width>1</width>
    <marked>false</marked>
    <xfill>false</xfill>
    <animation>0</animation>
    <name>phot_poly.drawing</name>
    <source>410/0@1</source>
</properties>
<properties>
    <frame-color>#ff0000</frame-color>
    <fill-color>#ff0000</fill-color>
    <frame-brightness>0</frame-brightness>
    <fill-brightness>0</fill-brightness>
    <dither-pattern>I9</dither-pattern>
    <line-style/>
    <valid>true</valid>
    <visible>true</visible>
    <transparent>false</transparent>
    <width>1</width>
    <marked>false</marked>
    <xfill>false</xfill>
    <animation>0</animation>
    <name>phot_pwell.drawing</name>
    <source>420/0@1</source>
</properties>
<properties>
    <frame-color>#0000ff</frame-color>
    <fill-color>#0000ff</fill-color>
    <frame-brightness>0</frame-brightness>
    <fill-brightness>0</fill-brightness>
    <dither-pattern>I5</dither-pattern>
    <line-style/>
    <valid>true</valid>
    <visible>true</visible>
    <transparent>false</transparent>
    <width>1</width>
    <marked>false</marked>
    <xfill>false</xfill>
    <animation>0</animation>
    <name>phot_nwell.drawing</name>
    <source>430/0@1</source>
</properties>
<properties>
    <frame-color>#ff0000</frame-color>
    <fill-color>#ff0000</fill-color>
    <frame-brightness>0</frame-brightness>
    <fill-brightness>0</fill-brightness>
    <dither-pattern>I11</dither-pattern>
    <line-style/>
    <valid>true</valid>
    <visible>true</visible>
    <transparent>false</transparent>
    <width>1</width>
    <marked>false</marked>
    <xfill>false</xfill>
    <animation>0</animation>
    <name>phot_pimplant.drawing</name>
    <source>440/0@1</source>
</properties>
<properties>
    <frame-color>#0000ff</frame-color>
    <fill-color>#0000ff</fill-color>
    <frame-brightness>0</frame-brightness>
    <fill-brightness>0</fill-brightness>
    <dither-pattern>I7</dither-pattern>
    <line-style/>
    <valid>true</valid>
    <visible>true</visible>
    <transparent>false</transparent>
    <width>1</width>
    <marked>false</marked>
    <xfill>false</xfill>
    <animation>0</animation>
    <name>phot_nimplant.drawing</name>
    <source>450/0@1</source>
</properties>
```

Put this block between the last properties block but befor the end of the name block.

## Import of example Vias

Importing a .LEF will create the layerproperties. The layerproperties are the layer-purpose-pairs of KLayout. When using the lef import script built into
KLayout, it will automatically load example vias into a new layout. Unfortunately, the layers are not the correct layers from the technology files.
The layers can be edited by selecting a layer in the layers sub-window and then editing the layer via Edit ‣ Layer ‣ Edit Layer Specification.
Recommended place is in the ~/.klayout/tech/libraries or if using a package: ~/.klayout/salt/<package-name>/tech/libraries. These will automatically be loaded and are available as static cells for insert or in PCells.

## Layermap

The .layermap file is usually supplied by the foundry. This file can be used in the pcell_lib_ext to use layernames instead of layer numbers in the PCell Library.
It contains layername | layernumber | layerdatatype on each line for each layer. They have to be separated by white spaces. Afterwards, they can by used by the self.add_layer(str varname, str layername)
function during the __init__ of a new class of a PCell. Later the layer is accessible as self.varname.

Recommended place is again in the tech folder.
