"""Brep plugin registrations for COMPAS."""

from collections.abc import Sequence
from os import PathLike
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import cast

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas.datastructures import Mesh
    from compas.geometry import Box
    from compas.geometry import Brep
    from compas.geometry import BrepEdge
    from compas.geometry import BrepFace
    from compas.geometry import BrepLoop
    from compas.geometry import BrepTrim
    from compas.geometry import BrepVertex
    from compas.geometry import Curve
    from compas.geometry import Cylinder
    from compas.geometry import Frame
    from compas.geometry import Plane
    from compas.geometry import Point
    from compas.geometry import Polygon
    from compas.geometry import Polyline
    from compas.geometry import Sphere
    from compas.geometry import Tessellation
    from compas.geometry import Torus
    from compas.geometry import Transformation
    from compas.geometry import Vector


def _occ(brep):
    from compas_occ.brep import OCCBrep

    if isinstance(brep, OCCBrep):
        return brep
    return OCCBrep.from_native(brep.native_brep)


def _wrap(brep):
    from compas.geometry import Brep

    return Brep(native_brep=brep.native_brep)


def _factory(method, *args, **kwargs):
    from compas_occ.brep import OCCBrep

    return _wrap(getattr(OCCBrep, method)(*args, **kwargs))


def _occ_curves(curves):
    from compas_occ.geometry import OCCNurbsCurve

    return [curve if isinstance(curve, OCCNurbsCurve) else OCCNurbsCurve.from_native(curve.native_curve) for curve in curves]


def _occ_breps(value):
    if isinstance(value, (list, tuple)):
        return [_occ(item) for item in value]
    return _occ(value)


def _unique(items):
    unique = []
    for item in items:
        if not any(item.is_same(other) for other in unique):
            unique.append(item)
    return unique


@plugin(category="brep-factories", requires=["OCC"])
def from_box(box: "Box") -> "Brep":
    return _factory("from_box", box)


@plugin(category="brep-factories", requires=["OCC"])
def from_brepfaces(faces: Sequence["BrepFace"]) -> "Brep":
    return _factory("from_brepfaces", faces)


@plugin(category="brep-factories", requires=["OCC"])
def from_cylinder(cylinder: "Cylinder") -> "Brep":
    return _factory("from_cylinder", cylinder)


@plugin(category="brep-factories", requires=["OCC"])
def from_extrusion(curve: "Curve | Polyline", vector: "Vector", cap_ends: bool = True) -> "Brep":
    return _factory("from_extrusion", curve, vector, cap_ends=cap_ends)


@plugin(category="brep-factories", requires=["OCC"])
def from_mesh(mesh: "Mesh") -> "Brep":
    return _factory("from_mesh", mesh)


@plugin(category="brep-factories", requires=["OCC"])
def from_plane(
    plane: "Plane",
    domain_u: tuple[float, float] = (-1, 1),
    domain_v: tuple[float, float] = (-1, 1),
) -> "Brep":
    return _factory("from_plane", plane, domain_u=domain_u, domain_v=domain_v)


@plugin(category="brep-factories", requires=["OCC"])
def from_planes(planes: Sequence["Plane"]) -> "Brep":
    return _factory("from_planes", planes)


@plugin(category="brep-factories", requires=["OCC"])
def from_polygons(polygons: Sequence["Polygon"], *args: Any, **kwargs: Any) -> "Brep":
    return _factory("from_polygons", polygons, *args, **kwargs)


@plugin(category="brep-factories", requires=["OCC"])
def from_sphere(sphere: "Sphere") -> "Brep":
    return _factory("from_sphere", sphere)


@plugin(category="brep-factories", requires=["OCC"])
def from_sweep(profile: "BrepEdge | BrepFace", path: "BrepLoop", *args: Any, **kwargs: Any) -> "Brep":
    return _factory("from_sweep", profile, path, *args, **kwargs)


@plugin(category="brep-factories", requires=["OCC"])
def from_torus(torus: "Torus") -> "Brep":
    return _factory("from_torus", torus)


@plugin(category="brep-factories", requires=["OCC"])
def from_breps(breps: Sequence["Brep"], *args: Any, **kwargs: Any) -> "Brep":
    return _factory("from_breps", [_occ(brep) for brep in breps], *args, **kwargs)


@plugin(category="brep-factories", requires=["OCC"])
def from_loft(curves: Sequence["Curve"]) -> "Brep":
    return _factory("from_loft", _occ_curves(curves))


@plugin(category="brep-factories", requires=["OCC"])
def from_native(native_brep: Any) -> "Brep":
    return _factory("from_native", native_brep)


@plugin(category="brep-io", requires=["OCC"])
def from_iges(filename: str | PathLike[str]) -> "Brep":
    return _factory("from_iges", filename)


@plugin(category="brep-io", requires=["OCC"])
def from_step(filename: str | PathLike[str]) -> "Brep":
    return _factory("from_step", filename)


@plugin(category="brep-operations", requires=["OCC"])
def from_boolean_difference(brep_a: "Brep | list[Brep]", brep_b: "Brep | list[Brep]") -> "Brep":
    return _factory("from_boolean_difference", _occ_breps(brep_a), _occ_breps(brep_b))


@plugin(category="brep-operations", requires=["OCC"])
def from_boolean_intersection(brep_a: "Brep | list[Brep]", brep_b: "Brep | list[Brep]") -> "Brep":
    return _factory("from_boolean_intersection", _occ_breps(brep_a), _occ_breps(brep_b))


@plugin(category="brep-operations", requires=["OCC"])
def from_boolean_union(brep_a: "Brep | list[Brep]", brep_b: "Brep | list[Brep]") -> "Brep":
    return _factory("from_boolean_union", _occ_breps(brep_a), _occ_breps(brep_b))


@plugin(category="brep-serialization", requires=["OCC"])
def brep_to_data(brep: "Brep") -> dict[str, Any]:
    return _occ(brep).to_data(include_native=True)


@plugin(category="brep-serialization", requires=["OCC"])
def brep_rebuild(brep: "Brep", data: dict[str, Any]) -> None:
    from compas_occ.brep import OCCBrep

    rebuilt = OCCBrep.from_data(data)
    brep._native_brep = rebuilt.native_brep


@plugin(category="brep-queries", requires=["OCC"])
def brep_area(brep: "Brep") -> float:
    return _occ(brep).area


@plugin(category="brep-queries", requires=["OCC"])
def brep_aabb(brep: "Brep") -> "Box":
    return _occ(brep).aabb


@plugin(category="brep-queries", requires=["OCC"])
def brep_centroid(brep: "Brep") -> "Point":
    return _occ(brep).centroid


@plugin(category="brep-queries", requires=["OCC"])
def brep_frame(brep: "Brep") -> "Frame":
    return _occ(brep).frame


@plugin(category="brep-queries", requires=["OCC"])
def brep_obb(brep: "Brep") -> "Box":
    return _occ(brep).obb


@plugin(category="brep-queries", requires=["OCC"])
def brep_volume(brep: "Brep") -> float:
    return _occ(brep).volume


@plugin(category="brep-queries", requires=["OCC"])
def brep_orientation(brep: "Brep") -> Literal[0, 1, 2, 3]:
    return cast(Literal[0, 1, 2, 3], int(_occ(brep).orientation))


@plugin(category="brep-queries", requires=["OCC"])
def brep_type(brep: "Brep") -> Literal[0, 1, 2, 3, 4, 5, 6, 7, 8]:
    return cast(Literal[0, 1, 2, 3, 4, 5, 6, 7, 8], int(_occ(brep).type))


@plugin(category="brep-queries", requires=["OCC"])
def brep_is_valid(brep: "Brep") -> bool:
    return _occ(brep).is_valid


@plugin(category="brep-queries", requires=["OCC"])
def brep_is_orientable(brep: "Brep") -> bool:
    raise NotImplementedError("OCC does not compute whether a BRep is orientable.")


@plugin(category="brep-queries", requires=["OCC"])
def brep_is_closed(brep: "Brep") -> bool:
    raise NotImplementedError("OCC does not compute whether a BRep has naked boundaries.")


@plugin(category="brep-queries", requires=["OCC"])
def brep_is_infinite(brep: "Brep") -> bool:
    raise NotImplementedError("OCC does not compute whether a BRep is infinite.")


@plugin(category="brep-queries", requires=["OCC"])
def brep_is_convex(brep: "Brep") -> bool:
    raise NotImplementedError("OCC does not compute whether a BRep is convex.")


@plugin(category="brep-queries", requires=["OCC"])
def brep_is_manifold(brep: "Brep") -> bool:
    raise NotImplementedError("OCC does not compute whether a BRep is manifold.")


@plugin(category="brep-queries", requires=["OCC"])
def brep_is_surface(brep: "Brep") -> bool:
    from OCC.Core.TopAbs import TopAbs_FACE

    return _occ(brep).type == TopAbs_FACE


@plugin(category="brep-queries", requires=["OCC"])
def brep_is_compound(brep: "Brep") -> bool:
    return _occ(brep).is_compound


@plugin(category="brep-queries", requires=["OCC"])
def brep_is_compoundsolid(brep: "Brep") -> bool:
    return _occ(brep).is_compoundsolid


@plugin(category="brep-queries", requires=["OCC"])
def brep_is_shell(brep: "Brep") -> bool:
    return _occ(brep).is_shell


@plugin(category="brep-queries", requires=["OCC"])
def brep_is_solid(brep: "Brep") -> bool:
    return _occ(brep).is_solid


@plugin(category="brep-queries", requires=["OCC"])
def brep_vertices(brep: "Brep") -> list["BrepVertex"]:
    return _unique(_occ(brep).vertices)


@plugin(category="brep-queries", requires=["OCC"])
def brep_edges(brep: "Brep") -> list["BrepEdge"]:
    return _unique(_occ(brep).edges)


@plugin(category="brep-queries", requires=["OCC"])
def brep_trims(brep: "Brep") -> list["BrepTrim"]:
    raise NotImplementedError("OCC does not provide a BRep trim representation.")


@plugin(category="brep-queries", requires=["OCC"])
def brep_loops(brep: "Brep") -> list["BrepLoop"]:
    return _unique(_occ(brep).loops)


@plugin(category="brep-queries", requires=["OCC"])
def brep_faces(brep: "Brep") -> list["BrepFace"]:
    return _unique(_occ(brep).faces)


@plugin(category="brep-queries", requires=["OCC"])
def brep_shells(brep: "Brep") -> list["Brep"]:
    return [_wrap(shell) for shell in _occ(brep).shells]


@plugin(category="brep-queries", requires=["OCC"])
def brep_solids(brep: "Brep") -> list["Brep"]:
    return [_wrap(solid) for solid in _occ(brep).solids]


@plugin(category="brep-operations", requires=["OCC"])
def brep_to_tessellation(
    brep: "Brep",
    *,
    linear_deflection: float,
    angular_deflection: float,
) -> "Tessellation":
    return _occ(brep).to_tessellation(
        linear_deflection=linear_deflection,
        angular_deflection=angular_deflection,
    )


@plugin(category="brep-operations", requires=["OCC"])
def brep_fillet(brep: "Brep", radius: float, exclude: Sequence["BrepEdge"] | None = None) -> "Brep":
    edges = cast(Any, list(exclude)) if exclude is not None else None
    return _wrap(_occ(brep).filleted(radius, exclude=edges))


def _copy_and_apply(brep, method, *args, **kwargs):
    result = _occ(brep).copy()
    getattr(result, method)(*args, **kwargs)
    return _wrap(result)


@plugin(category="brep-operations", requires=["OCC"])
def brep_copy(brep: "Brep") -> "Brep":
    return _wrap(_occ(brep).copy())


@plugin(category="brep-operations", requires=["OCC"])
def brep_transform(brep: "Brep", transformation: "Transformation") -> None:
    transformed = _occ(brep)
    transformed.transform(transformation)
    brep._native_brep = transformed.native_brep


@plugin(category="brep-operations", requires=["OCC"])
def brep_fix(brep: "Brep") -> "Brep":
    return _copy_and_apply(brep, "fix")


@plugin(category="brep-operations", requires=["OCC"])
def brep_flip(brep: "Brep") -> "Brep":
    result = _occ(brep).copy()
    result.occ_shape.Reverse()
    return _wrap(result)


@plugin(category="brep-operations", requires=["OCC"])
def brep_heal(brep: "Brep") -> "Brep":
    return _copy_and_apply(brep, "heal")


@plugin(category="brep-operations", requires=["OCC"])
def brep_make_solid(brep: "Brep") -> "Brep":
    return _copy_and_apply(brep, "make_solid")


@plugin(category="brep-operations", requires=["OCC"])
def brep_overlap(
    brep_a: "Brep",
    brep_b: "Brep",
    linear_deflection: float | None = None,
    angular_deflection: float | None = None,
    tolerance: float = 0.0,
    relative: bool = False,
) -> tuple[list["BrepFace"], list["BrepFace"]]:
    return cast(
        tuple[list["BrepFace"], list["BrepFace"]],
        _occ(brep_a).overlap(
            _occ(brep_b),
            linear_deflection=linear_deflection,
            angular_deflection=angular_deflection,
            tolerance=tolerance,
            relative=relative,
        ),
    )


@plugin(category="brep-operations", requires=["OCC"])
def brep_sew(brep: "Brep") -> "Brep":
    return _copy_and_apply(brep, "sew")


@plugin(category="brep-operations", requires=["OCC"])
def brep_slice(brep: "Brep", plane: "Plane | Frame") -> "Brep | None":
    result = _occ(brep).slice(cast("Plane", plane))
    return _wrap(result) if result else None


@plugin(category="brep-operations", requires=["OCC"])
def brep_split(brep: "Brep", cutter: "Brep") -> list["Brep"]:
    return [_wrap(result) for result in _occ(brep).split(_occ(cutter))]


@plugin(category="brep-operations", requires=["OCC"])
def brep_trimmed(brep: "Brep", plane: "Plane | Frame") -> "Brep":
    return _wrap(_occ(brep).trimmed(cast("Plane", plane)))


@plugin(category="brep-io", requires=["OCC"])
def brep_to_iges(brep: "Brep", filepath: str | PathLike[str]) -> bool:
    return _occ(brep).to_iges(filepath)


@plugin(category="brep-io", requires=["OCC"])
def brep_to_step(brep: "Brep", filepath: str | PathLike[str]) -> None:
    _occ(brep).to_step(filepath)


@plugin(category="brep-io", requires=["OCC"])
def brep_to_stl(brep: "Brep", filepath: str | PathLike[str]) -> bool:
    return _occ(brep).to_stl(filepath)
