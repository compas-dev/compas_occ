"""Versioned JSON data conversion for OCC boundary representations."""

import base64
import os
import tempfile
from typing import Optional

from OCC.Core import BRep
from OCC.Core import BRepTools
from OCC.Core import TopAbs
from OCC.Core import TopoDS

BREP_SCHEMA = "compas.brep"
BREP_SCHEMA_VERSION = 1


def brep_to_data(brep, include_native: bool = False, units: Optional[str] = None) -> dict:
    """Convert an OCC BRep to versioned, JSON-compatible data."""
    data = {
        "schema": BREP_SCHEMA,
        "version": BREP_SCHEMA_VERSION,
        "units": units,
        "geometry": {
            "representation": "embedded",
        },
        "topology": {
            "representation": "components",
            "shape_type": int(brep.type),
            "components": _component_data(brep),
        },
    }
    if include_native:
        data["native"] = encode_native_brep(brep.occ_shape)
    return data


def brep_from_data(data: dict, prefer_native: bool = True, validate: bool = True, heal: bool = False):
    """Construct an OCC BRep from versioned or legacy serialization data."""
    from .brep import OCCBrep
    from .builder import OCCBrepBuilder

    if not isinstance(data, dict):
        raise TypeError("BRep data should be a dictionary.")

    native = data.get("native")
    if prefer_native and native is not None:
        brep = OCCBrep.from_native(decode_native_brep(native))
    else:
        components = _components_from_data(data)
        breps = []
        for component in components:
            shape_type = component["shape_type"]
            faces = component["faces"]
            make_solid = shape_type == int(TopAbs.TopAbs_SOLID)
            rebuilt = OCCBrepBuilder(make_solid=make_solid, heal=heal).build(faces)
            if shape_type == int(TopAbs.TopAbs_FACE):
                if len(rebuilt.faces) != 1:
                    raise ValueError("A serialized face component should contain exactly one face.")
                rebuilt = OCCBrep.from_native(rebuilt.faces[0].occ_face)
            breps.append(rebuilt)
        if not breps:
            raise ValueError("The serialized BRep contains no topology components.")
        brep = breps[0] if len(breps) == 1 else OCCBrep.from_breps(breps)

    if validate and not brep.is_valid:
        raise ValueError("The serialized BRep does not define a valid shape.")
    return brep


def encode_native_brep(shape: TopoDS.TopoDS_Shape) -> dict:
    """Encode an OCC shape as a Base64 Open CASCADE BREP payload."""
    filepath = _temporary_path()
    try:
        if not BRepTools.breptools.Write(shape, filepath):
            raise ValueError("The native OCC BREP payload could not be written.")
        with open(filepath, "rb") as stream:
            payload = base64.b64encode(stream.read()).decode("ascii")
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)
    return {
        "backend": "occ",
        "format": "brep",
        "encoding": "base64",
        "data": payload,
    }


def decode_native_brep(data: dict) -> TopoDS.TopoDS_Shape:
    """Decode a Base64 Open CASCADE BREP payload."""
    if not isinstance(data, dict):
        raise TypeError("The native BRep payload should be a dictionary.")
    expected = ("occ", "brep", "base64")
    actual = (data.get("backend"), data.get("format"), data.get("encoding"))
    if actual != expected:
        raise ValueError("Unsupported native BRep payload: {!r}.".format(actual))
    try:
        payload = base64.b64decode(data["data"], validate=True)
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("The native BRep payload is not valid Base64 data.") from error

    filepath = _temporary_path()
    try:
        with open(filepath, "wb") as stream:
            stream.write(payload)
        shape = TopoDS.TopoDS_Shape()
        builder = BRep.BRep_Builder()
        if not BRepTools.breptools.Read(shape, filepath, builder):
            raise ValueError("The native OCC BREP payload could not be read.")
        return shape
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


def _components_from_data(data: dict) -> list[dict]:
    if "schema" not in data and "faces" in data:
        return [{"shape_type": int(TopAbs.TopAbs_SOLID), "faces": data["faces"]}]
    if data.get("schema") != BREP_SCHEMA:
        raise ValueError("Unsupported BRep schema: {!r}.".format(data.get("schema")))
    if data.get("version") != BREP_SCHEMA_VERSION:
        raise ValueError("Unsupported BRep schema version: {!r}.".format(data.get("version")))
    topology = data.get("topology")
    if not isinstance(topology, dict) or topology.get("representation") != "components":
        raise ValueError("BRep schema version 1 requires component-oriented topology data.")
    components = topology.get("components")
    if not isinstance(components, list):
        raise ValueError("BRep topology components should be a list.")
    for component in components:
        if not isinstance(component, dict) or not isinstance(component.get("faces"), list):
            raise ValueError("Each BRep topology component should contain a face list.")
        if not isinstance(component.get("shape_type"), int):
            raise ValueError("Each BRep topology component should contain an integer shape type.")
    return components


def _component_data(brep) -> list[dict]:
    if brep.is_compound or brep.is_compoundsolid:
        components = brep.solids or brep.shells
    else:
        components = [brep]
    return [
        {
            "shape_type": int(component.type),
            "faces": [face.__data__ for face in component.faces],
        }
        for component in components
    ]


def _temporary_path() -> str:
    descriptor, filepath = tempfile.mkstemp(suffix=".brep")
    os.close(descriptor)
    return filepath
