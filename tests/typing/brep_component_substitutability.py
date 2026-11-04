from typing import assert_type
from typing import cast

from compas.geometry import BrepEdge
from compas.geometry import BrepFace
from compas.geometry import BrepLoop
from compas.geometry import BrepVertex
from compas.geometry import Curve
from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas_occ.brep import OCCBrepEdge
from compas_occ.brep import OCCBrepFace
from compas_occ.brep import OCCBrepLoop
from compas_occ.brep import OCCBrepVertex


def consume_vertex(vertex: BrepVertex) -> None:
    assert_type(vertex.point, Point)


def consume_edge(edge: BrepEdge) -> None:
    assert_type(edge.vertices, list[BrepVertex])
    assert_type(edge.first_vertex, BrepVertex)
    assert_type(edge.last_vertex, BrepVertex)


def consume_loop(loop: BrepLoop) -> None:
    assert_type(loop.vertices, list[BrepVertex])
    assert_type(loop.edges, list[BrepEdge])


def consume_face(face: BrepFace, loop: BrepLoop) -> None:
    assert_type(face.vertices, list[BrepVertex])
    assert_type(face.edges, list[BrepEdge])
    assert_type(face.loops, list[BrepLoop])
    assert_type(face.nurbssurface, NurbsSurface)
    assert_type(face.is_valid, bool)
    face.add_loop(loop, reverse=False)
    face.add_loops([loop], reverse=True)


occ_vertex = cast(OCCBrepVertex, object())
occ_edge = cast(OCCBrepEdge, object())
occ_loop = cast(OCCBrepLoop, object())
occ_face = cast(OCCBrepFace, object())
curve = cast(Curve, object())

consume_vertex(occ_vertex)
consume_edge(occ_edge)
consume_loop(occ_loop)
consume_face(occ_face, occ_loop)
assert_type(OCCBrepEdge.from_curve(curve), OCCBrepEdge)
assert_type(OCCBrepLoop.from_edges([occ_edge]), OCCBrepLoop)
