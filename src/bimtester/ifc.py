# BIMTester - OpenBIM Auditing Tool
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BIMTester.
#
# BIMTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BIMTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BIMTester.  If not, see <http://www.gnu.org/licenses/>.


import os
import time

import ifcopenshell
import ifcopenshell.util.element as eleutils
import ifcopenshell.util.selector


# ********************************************************************************************
class IfcStore:

    path = ""
    basename = ""
    dirpath = ""
    basedir = ""
    file = None
    prjnr = ""

    bookmarks = {}

    elements = {}
    materials = {}
    layernames = {}

    new_props = {}  # ist it used somewhere, as class variable ???
    psets = {}
    qsets = {}

    geom_freecad_shape = {}
    geom_has_elements = {}
    geom_has_errors = {}


# obiges sind class attributes not instance attributes 
# be carefull
# class attributes are shared betweeen all instances of this class
# thus defined somewhere they are available if the class is imported somewhere eles
# defined in run but imported in a feature ... 
# https://www.geeksforgeeks.org/python/python-attributes-class-vs-instance-explained/
# oben ist super erlaeutert und super vergleichstabelle, unten ist auch gut
# https://builtin.com/software-engineering-perspectives/python-attributes


# da in diesem modul auch die klasse IfcStore definiert ist
# kann in unteren methoden direkt auf die klassenvariablen zugegriffen werden
# lesend und schreibend


# ********************************************************************************************
def init_ifcstore(ifc_file_path, elementfilter):

    time_start = time.process_time()

    if not os.path.isfile(ifc_file_path):
        print("IFC-file {} not found.".format(ifc_file_path))
        return False

    print("Parse IFC-file and processing IfcStore on {}".format(ifc_file_path))

    ifc_file_basename = os.path.basename(os.path.splitext(ifc_file_path)[0])
    ifc_file_dir = os.path.dirname(ifc_file_path)
    IfcStore.basename = ifc_file_basename
    IfcStore.dirpath = ifc_file_dir
    IfcStore.path = ifc_file_path
    IfcStore.basedir = os.path.basename(ifc_file_dir)

    IfcStore.file = ifcopenshell.open(str(ifc_file_path))  # just to be sure if a Path object was given
    # IfcStore.elements = IfcStore.file.by_type(elementfilter)  # noqa: F401 # type: ignore
    IfcStore.elements = list(ifcopenshell.util.selector.filter_elements(IfcStore.file, elementfilter))
    for elem in IfcStore.elements:
        IfcStore.psets[elem.id()] = get_psets_enums_as_scalar(IfcStore.file, elem)
        IfcStore.qsets[elem.id()] = eleutils.get_psets(elem, qtos_only=True)
        IfcStore.materials[elem.id()] = eleutils.get_material(elem)
        IfcStore.layernames[elem.id()] = get_layer_name(IfcStore.file, elem)

    output_some_information(elementfilter)

    print(
        "--> {} seconds. Time to parse IFC-file and do data analysis\n"
        .format(round((time.process_time() - time_start), 3))
    )
    # time.sleep(2)  # to be able ot read the parse time, not needed we write a log file

    # for elem in IfcStore.elements:
    #     print(elem)
    # print(IfcStore.elements)
    # print(type(IfcStore.elements))
    # ToDO sort elements list bei ifc entity nummer, geht nicht einfach so mit sorted :-(

    # exit()

    return True


# ********************************************************************************************
def output_some_information(elementfilter):

    print("The project: {}".format(IfcStore.file.by_type("IfcProject")[0]))
    print("{} {}".format(len(IfcStore.elements), elementfilter))
    print("{} IfcOpeningElements".format(len(IfcStore.file.by_type("IfcOpeningElement"))))
    print("{} All Elements".format(len(IfcStore.elements)))
    print("{} PSets".format(len(IfcStore.psets)))
    print("{} QSets".format(len(IfcStore.qsets)))
    print("{} Materials".format(len(IfcStore.materials)))
    print("{} Layer names".format(len(IfcStore.layernames)))
    print("")

    return True


# ************************************************************************************************
def get_psets_enums_as_scalar(ifcfile, elem):
    """
    eleutils.get_psets returns IfcPropertyEnumeratedValue always as a list,
    #135=IFCPROPERTYENUMERATEDVALUE('Status',$,(IFCLABEL('DEMOLISH')),$);
    --> {'Status': ['DEMOLISH']}
    Thus comparisons against 'DEMOLISH' fail.
    An enumerated value with exactly one value is returned as scalar --> {'Status': 'DEMOLISH'}
    IfcPropertyListValue and enums with more than one value stay lists.
    """
    psets = eleutils.get_psets(elem, psets_only=True)
    for pset in psets.values():
        pset_id = pset.get("id")
        if pset_id is None:
            continue
        pset_entity = ifcfile.by_id(pset_id)
        if not pset_entity.is_a("IfcPropertySet"):
            continue
        for prop in pset_entity.HasProperties or ():
            if not prop.is_a("IfcPropertyEnumeratedValue"):
                continue
            value = pset.get(prop.Name)
            if isinstance(value, (list, tuple)) and len(value) == 1:
                pset[prop.Name] = value[0]
    return psets


# ************************************************************************************************
def get_layer_name(ifcfile, elem):

    # None: elem has no layer assigned
    # "": layer name in IFC is None or ""
    # "xyz": the layer name

    #  print("")
    # print(elem)
    all_layer = eleutils.get_layers(ifcfile, elem)
    # print(all_layer)

    # workaround outside IfcOpenShell code for IFC4 and Allplan and IfcReinforcingBar
    if all_layer == [] and ifcfile.schema == "IFC4" and elem.is_a() == "IfcReinforcingBar":
        print("Allplan IFC4 reinforcement layerproblem. We get the layer ourself.")
        # print(elem.Representation)
        # print(elem.Representation.Representations[0])
        # print(elem.Representation.Representations[0].Items[0])
        # print(elem.Representation.Representations[0].Items[0].__dir__())
        # print(elem.Representation.Representations[0].Items[0].LayerAssignment)
        try:
            found_layers = elem.Representation.Representations[0].Items[0].LayerAssignment
            print(found_layers[0])
            all_layer = [found_layers[0]]
        except Exception:
            print(elem)
            print("Could not get layer of Allplan IFC4 reinforcement.")

    if len(all_layer) > 0:
        if all_layer[0].Name is None:
            name = ""
        else:
            name = all_layer[0].Name
    else:
        name = None
    # print(name)

    return name

# todo, implement a workaround for allplan reinforcement ifc4, make report, try latest ifcos
# make a simple example and post on github bugreport
