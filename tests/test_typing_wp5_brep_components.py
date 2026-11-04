from compas.geometry import BrepEdge
from compas.geometry import BrepFace
from compas.geometry import BrepLoop
from compas.geometry import BrepVertex
from compas.geometry import Point
from compas.geometry import Polygon
from compas_occ.brep import OCCBrepEdge
from compas_occ.brep import OCCBrepFace
from compas_occ.brep import OCCBrepLoop
from compas_occ.brep import OCCBrepVertex


def consume_vertex(vertex: BrepVertex) -> Point:
    return vertex.point


def consume_edge(edge: BrepEdge) -> list[BrepVertex]:
    return edge.vertices


def consume_loop(loop: BrepLoop) -> tuple[list[BrepVertex], list[BrepEdge]]:
    return loop.vertices, loop.edges


def consume_face(face: BrepFace) -> tuple[list[BrepVertex], list[BrepEdge], list[BrepLoop]]:
    return face.vertices, face.edges, face.loops


def test_brep_components_satisfy_core_consumer_contracts() -> None:
    polygon = Polygon.from_sides_and_radius_xy(4, 1.0)
    vertex = OCCBrepVertex.from_point(Point(0, 0, 0))
    edge = OCCBrepEdge.from_point_point(Point(0, 0, 0), Point(1, 0, 0))
    loop = OCCBrepLoop.from_polygon(polygon)
    face = OCCBrepFace.from_polygon(polygon)

    assert consume_vertex(vertex) == Point(0, 0, 0)
    assert len(consume_edge(edge)) == 2
    assert len(consume_loop(loop)[1]) == 4
    assert len(consume_face(face)[2]) == 1
    assert face.is_valid


def test_brep_components_expose_core_native_properties() -> None:
    polygon = Polygon.from_sides_and_radius_xy(4, 1.0)
    vertex = OCCBrepVertex.from_point(Point(0, 0, 0))
    edge = OCCBrepEdge.from_point_point(Point(0, 0, 0), Point(1, 0, 0))
    loop = OCCBrepLoop.from_polygon(polygon)
    face = OCCBrepFace.from_polygon(polygon)

    assert vertex.native_vertex.IsSame(vertex.native_vertex)
    assert edge.native_edge.IsSame(edge.native_edge)
    assert loop.native_loop.IsSame(loop.native_loop)
    assert face.native_face.IsSame(face.native_face)


def test_brep_component_equality_accepts_arbitrary_objects() -> None:
    vertex = OCCBrepVertex.from_point(Point(0, 0, 0))
    edge = OCCBrepEdge.from_point_point(Point(0, 0, 0), Point(1, 0, 0))

    assert vertex != object()
    assert edge != object()
