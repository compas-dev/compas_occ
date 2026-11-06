import pytest
import random
from math import pi
from math import radians

from OCC.Core import BRep
from OCC.Core import TopLoc
from OCC.Core.Geom import Geom_BezierCurve
from OCC.Core.Geom import Geom_Ellipse
from OCC.Core.Geom import Geom_Hyperbola
from OCC.Core.Geom import Geom_Parabola
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.gp import gp_Ax2
from OCC.Core.gp import gp_Dir
from OCC.Core.gp import gp_Pnt

from compas.geometry import Box
from compas.geometry import Brep
from compas.geometry import Circle
from compas.geometry import Cylinder
from compas.geometry import Frame
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.geometry import Plane
from compas.geometry import Polygon
from compas.geometry import Sphere
from compas.geometry import Tessellation
from compas.geometry import Vector
from compas.geometry import area_triangle
from compas.tolerance import TOL
from compas_occ.brep import OCCBrep
from compas_occ.brep import OCCBrepEdge
from compas_occ.brep import OCCBrepFace
from compas_occ.brep import OCCBrepLoop
from compas_occ.brep.errors import BrepTessellationError
from compas_occ.files import read_step
from compas_occ.files import read_iges
from compas_occ.files import read_brep
from compas_occ.files import write_step
from compas_occ.files import write_iges
from compas_occ.files import write_brep
from compas_occ.geometry import OCCNurbsCurve
from compas_occ.geometry import OCCCurve


@pytest.mark.parametrize(
    "box",
    [
        Box(1),
        Box(1, 2, 3),
        Box(random.random()),
        Box(random.random(), random.random(), random.random()),
        Box(1, frame=Frame(point=[random.random(), random.random(), random.random()])),
        Box(1, 2, 3, frame=Frame(point=[random.random(), random.random(), random.random()])),
        Box(random.random(), frame=Frame(point=[random.random(), random.random(), random.random()])),
        Box(random.random(), random.random(), random.random(), frame=Frame(point=[random.random(), random.random(), random.random()])),
    ],
)
def test_brep_from_box(box: Box):
    brep = OCCBrep.from_box(box)
    brep.heal()

    assert TOL.is_close(box.volume(), brep.volume)
    assert len(box.points) == len(brep.points)
    assert box.frame.point == brep.centroid
    # assert all(a == b for a, b in zip(box.points, box.points))


def test_brep_from_cylinder():
    cylinder = Cylinder(radius=1, height=1)
    brep = OCCBrep.from_cylinder(cylinder)

    assert TOL.is_close(cylinder.volume(), brep.volume)
    assert cylinder.frame.point == brep.centroid


def test_brep_from_sphere():
    sphere = Sphere(1)
    brep = OCCBrep.from_sphere(sphere)

    assert TOL.is_close(sphere.volume(), brep.volume)
    assert sphere.frame.point == brep.centroid


def test_brep_tessellation_uses_compas_tessellation(monkeypatch):
    from compas_occ.brep import brep as brep_module

    brep = OCCBrep.from_box(Box(1))
    calls = []
    incremental_mesh = brep_module.BRepMesh.BRepMesh_IncrementalMesh

    def capture_incremental_mesh(*args):
        calls.append(args)
        return incremental_mesh(*args)

    monkeypatch.setattr(brep_module.BRepMesh, "BRepMesh_IncrementalMesh", capture_incremental_mesh)

    tessellation = brep.to_tessellation(linear_deflection=0.01, angular_deflection=12.0)

    assert isinstance(tessellation, Tessellation)
    assert tessellation.number_of_vertices == 24
    assert tessellation.number_of_triangles == 12
    assert len(tessellation.polylines) == 12
    assert calls[0][1] == 0.01
    assert calls[0][3] == pytest.approx(radians(12.0))


def test_brep_tessellation_defaults_and_partial_defaults_reach_native_boundary(monkeypatch):
    from compas_occ.brep import brep as brep_module

    calls = []
    incremental_mesh = brep_module.BRepMesh.BRepMesh_IncrementalMesh

    def capture_incremental_mesh(*args):
        calls.append(args)
        return incremental_mesh(*args)

    monkeypatch.setattr(brep_module.BRepMesh, "BRepMesh_IncrementalMesh", capture_incremental_mesh)
    brep = Brep.from_box(Box(1))

    brep.to_tessellation()
    assert calls[-1][1] == TOL.lineardeflection
    assert calls[-1][3] == pytest.approx(TOL.angulardeflection)

    brep.to_tessellation(linear_deflection=0.04)
    assert calls[-1][1] == 0.04
    assert calls[-1][3] == pytest.approx(TOL.angulardeflection)

    brep.to_tessellation(angular_deflection=9.0)
    assert calls[-1][1] == TOL.lineardeflection
    assert calls[-1][3] == pytest.approx(radians(9.0))

    with TOL.temporary(lineardeflection=0.07, angulardeflection=radians(11.0)):
        brep.to_tessellation()
        assert calls[-1][1] == 0.07
        assert calls[-1][3] == pytest.approx(radians(11.0))


def test_brep_tessellation_returns_fresh_results_without_mutating_source():
    brep = Brep.from_box(Box(1))
    native_brep = brep.native_brep
    area = brep.area
    volume = brep.volume

    first = brep.to_tessellation(linear_deflection=0.01, angular_deflection=12.0)
    second = brep.to_tessellation(linear_deflection=0.01, angular_deflection=12.0)

    assert first is not second
    assert first.vertices is not second.vertices
    assert first.triangles is not second.triangles
    assert brep.native_brep.IsSame(native_brep)
    assert brep.area == area
    assert brep.volume == volume


def test_brep_tessellation_does_not_cache_native_mesh_on_source():
    def triangulations(brep):
        tool = BRep.BRep_Tool()
        result = []
        for face in brep.faces:
            location = TopLoc.TopLoc_Location()
            result.append(tool.Triangulation(face.occ_face, location))
        return result

    brep = OCCBrep.from_sphere(Sphere(1))
    assert all(triangulation is None for triangulation in triangulations(brep))

    fine = brep.to_tessellation(linear_deflection=0.01, angular_deflection=20.0)
    coarse_after_fine = brep.to_tessellation(linear_deflection=0.1, angular_deflection=20.0)
    fresh_coarse = OCCBrep.from_sphere(Sphere(1)).to_tessellation(linear_deflection=0.1, angular_deflection=20.0)

    assert fine.number_of_triangles > coarse_after_fine.number_of_triangles
    assert coarse_after_fine.number_of_triangles == fresh_coarse.number_of_triangles
    assert all(triangulation is None for triangulation in triangulations(brep))


@pytest.mark.parametrize(
    ("keyword", "value", "error"),
    [
        ("linear_deflection", True, TypeError),
        ("linear_deflection", "0.01", TypeError),
        ("angular_deflection", False, TypeError),
        ("angular_deflection", object(), TypeError),
        ("linear_deflection", float("nan"), ValueError),
        ("linear_deflection", float("inf"), ValueError),
        ("linear_deflection", float("-inf"), ValueError),
        ("angular_deflection", float("nan"), ValueError),
        ("angular_deflection", float("inf"), ValueError),
        ("angular_deflection", float("-inf"), ValueError),
        ("linear_deflection", 0.0, ValueError),
        ("linear_deflection", -0.01, ValueError),
        ("angular_deflection", 0.0, ValueError),
        ("angular_deflection", -1.0, ValueError),
        ("angular_deflection", 180.0001, ValueError),
    ],
)
def test_brep_tessellation_validates_before_native_dispatch(monkeypatch, keyword, value, error):
    from compas_occ.brep import brep as brep_module

    calls = []

    def capture_incremental_mesh(*args):
        calls.append(args)
        raise AssertionError("Native meshing should not be called for invalid values.")

    monkeypatch.setattr(brep_module.BRepMesh, "BRepMesh_IncrementalMesh", capture_incremental_mesh)
    brep = Brep.from_box(Box(1))

    with pytest.raises(error):
        brep.to_tessellation(**{keyword: value})

    assert not calls


def test_brep_tessellation_preserves_reversed_shape_winding():
    def signed_volume(tessellation):
        volume = 0.0
        for a, b, c in tessellation.triangles:
            va = tessellation.vertices[a]
            vb = tessellation.vertices[b]
            vc = tessellation.vertices[c]
            volume += va[0] * (vb[1] * vc[2] - vb[2] * vc[1])
            volume += va[1] * (vb[2] * vc[0] - vb[0] * vc[2])
            volume += va[2] * (vb[0] * vc[1] - vb[1] * vc[0])
        return volume / 6.0

    brep = OCCBrep.from_box(Box(1))
    reversed_brep = OCCBrep.from_native(brep.native_brep.Reversed())
    assert signed_volume(brep.to_tessellation(linear_deflection=0.01, angular_deflection=12.0)) == pytest.approx(1.0)
    assert signed_volume(reversed_brep.to_tessellation(linear_deflection=0.01, angular_deflection=12.0)) == pytest.approx(-1.0)


def test_brep_tessellation_keeps_face_local_seam_vertices():
    brep = OCCBrep.from_box(Box(1))
    tessellation = brep.to_tessellation(linear_deflection=0.01, angular_deflection=12.0)
    coordinate_counts = {tuple(vertex): 0 for vertex in tessellation.vertices}

    for vertex in tessellation.vertices:
        coordinate_counts[tuple(vertex)] += 1

    assert tessellation.number_of_vertices == 24
    assert len(coordinate_counts) == 8
    assert set(coordinate_counts.values()) == {3}
    assert not tessellation.to_polygonal_surface().is_closed


def test_brep_tessellation_refines_for_smaller_deflection():
    coarse = OCCBrep.from_sphere(Sphere(1)).to_tessellation(linear_deflection=0.1, angular_deflection=20.0)
    fine = OCCBrep.from_sphere(Sphere(1)).to_tessellation(linear_deflection=0.01, angular_deflection=20.0)

    assert fine.number_of_triangles > coarse.number_of_triangles


def test_brep_tessellation_falls_back_when_edge_polygon_is_unavailable(monkeypatch):
    from compas_occ.brep import brep as brep_module

    brep = OCCBrep.from_box(Box(1))
    brep_tool = brep_module.BRep.BRep_Tool

    class ToolWithoutEdgePolygons:
        def __init__(self):
            self.tool = brep_tool()

        @staticmethod
        def Pnt(*args):
            return brep_tool.Pnt(*args)

        def Triangulation(self, *args):
            return self.tool.Triangulation(*args)

        def PolygonOnTriangulation(self, *args):
            return None

    monkeypatch.setattr(brep_module.BRep, "BRep_Tool", ToolWithoutEdgePolygons)

    tessellation = brep.to_tessellation(linear_deflection=0.01, angular_deflection=12.0)

    assert tessellation.number_of_triangles == 12
    assert len(tessellation.polylines) == 12
    assert all(len(polyline) == 2 for polyline in tessellation.polylines)


def test_brep_tessellation_fallback_samples_trimmed_conic_domain_and_orientation():
    from compas_occ.brep import brep as brep_module

    edge = OCCBrepEdge.from_circle(Circle(1.0), params=(0.0, 0.5 * pi))
    points = brep_module._fallback_edge_polyline(edge)

    assert len(points) == 129
    assert points[0] == edge.first_vertex.point
    assert points[-1] == edge.last_vertex.point
    assert list(points[64]) == pytest.approx([2**-0.5, 2**-0.5, 0.0])

    reversed_edge = OCCBrepEdge(edge.native_edge.Reversed())
    reversed_points = brep_module._fallback_edge_polyline(reversed_edge)

    assert reversed_points[0] == reversed_edge.first_vertex.point
    assert reversed_points[-1] == reversed_edge.last_vertex.point
    assert reversed_points == list(reversed(points))


def test_brep_tessellation_fallback_preserves_reversed_periodic_edge_orientation():
    from compas_occ.brep import brep as brep_module

    edge = OCCBrepEdge.from_circle(Circle(1.0))
    points = brep_module._fallback_edge_polyline(edge)
    reversed_edge = OCCBrepEdge(edge.native_edge.Reversed())
    reversed_points = brep_module._fallback_edge_polyline(reversed_edge)

    assert reversed_points == list(reversed(points))


def test_brep_tessellation_fallback_samples_every_supported_curve_type_over_edge_domain():
    from compas_occ.brep import brep as brep_module

    axis = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    poles = TColgp_Array1OfPnt(1, 3)
    poles.SetValue(1, gp_Pnt(0.0, 0.0, 0.0))
    poles.SetValue(2, gp_Pnt(1.0, 2.0, 0.0))
    poles.SetValue(3, gp_Pnt(2.0, 0.0, 0.0))

    curves = [
        OCCCurve.from_occ(Geom_Ellipse(axis, 2.0, 1.0)),
        OCCCurve.from_occ(Geom_Hyperbola(axis, 2.0, 1.0)),
        OCCCurve.from_occ(Geom_Parabola(axis, 1.0)),
        OCCCurve.from_occ(Geom_BezierCurve(poles)),
        OCCNurbsCurve.from_points([Point(0.0, 0.0, 0.0), Point(1.0, 2.0, 0.0), Point(2.0, 0.0, 0.0)]),
    ]

    for curve in curves:
        edge = OCCBrepEdge.from_curve(curve, params=(0.1, 0.9))
        points = brep_module._fallback_edge_polyline(edge)
        midpoint = edge.occ_adaptor.Value(0.5)

        assert len(points) == 129
        assert points[0] == edge.first_vertex.point
        assert points[-1] == edge.last_vertex.point
        assert list(points[64]) == pytest.approx([midpoint.X(), midpoint.Y(), midpoint.Z()])


def test_brep_tessellation_fallback_rejects_unsupported_edge_type():
    from compas_occ.brep import brep as brep_module

    class UnsupportedEdge:
        is_line = False
        is_circle = False
        is_ellipse = False
        is_hyperbola = False
        is_parabola = False
        is_bezier = False
        is_bspline = False
        type = 7

    with pytest.raises(BrepTessellationError, match="does not support edge curve type 7"):
        brep_module._fallback_edge_polyline(UnsupportedEdge())


def test_brep_tessellation_fallback_reports_sampling_failure():
    from compas_occ.brep import brep as brep_module

    class FailingAdaptor:
        def Value(self, parameter):
            raise RuntimeError("sampling failed")

    class FailingEdge:
        is_line = False
        is_circle = True
        is_ellipse = False
        is_hyperbola = False
        is_parabola = False
        is_bezier = False
        is_bspline = False
        type = 1
        domain = (0.0, 1.0)
        occ_adaptor = FailingAdaptor()

    with pytest.raises(BrepTessellationError, match="could not sample boundary edge curve type 1"):
        brep_module._fallback_edge_polyline(FailingEdge())


def test_brep_tessellation_reports_meshing_failure(monkeypatch):
    from compas_occ.brep import brep as brep_module

    class FailedMesher:
        def __init__(self, *args):
            pass

        def IsDone(self):
            return False

        def GetStatusFlags(self):
            return 17

    monkeypatch.setattr(brep_module.BRepMesh, "BRepMesh_IncrementalMesh", FailedMesher)

    with pytest.raises(BrepTessellationError, match="failed with status 17"):
        OCCBrep.from_box(Box(1)).to_tessellation(linear_deflection=0.01, angular_deflection=12.0)


def test_brep_tessellation_wraps_native_mesher_construction_failure(monkeypatch):
    from compas_occ.brep import brep as brep_module

    def failing_mesher(*args):
        raise RuntimeError("Standard_Failure: mesher construction failed")

    monkeypatch.setattr(brep_module.BRepMesh, "BRepMesh_IncrementalMesh", failing_mesher)

    with pytest.raises(BrepTessellationError, match="could not start BRep meshing") as caught:
        OCCBrep.from_box(Box(1)).to_tessellation(linear_deflection=0.01, angular_deflection=12.0)

    assert isinstance(caught.value.__cause__, RuntimeError)
    assert "Standard_Failure" in str(caught.value.__cause__)


@pytest.mark.parametrize("failing_method", ["IsDone", "GetStatusFlags"])
def test_brep_tessellation_wraps_native_mesher_status_failure(monkeypatch, failing_method):
    from compas_occ.brep import brep as brep_module

    class FailingStatusMesher:
        def __init__(self, *args):
            pass

        def IsDone(self):
            if failing_method == "IsDone":
                raise RuntimeError("Standard_Failure: completion status failed")
            return True

        def GetStatusFlags(self):
            if failing_method == "GetStatusFlags":
                raise RuntimeError("Standard_Failure: status flags failed")
            return 0

    monkeypatch.setattr(brep_module.BRepMesh, "BRepMesh_IncrementalMesh", FailingStatusMesher)

    with pytest.raises(BrepTessellationError, match="could not report BRep meshing status") as caught:
        OCCBrep.from_box(Box(1)).to_tessellation(linear_deflection=0.01, angular_deflection=12.0)

    assert isinstance(caught.value.__cause__, RuntimeError)
    assert "Standard_Failure" in str(caught.value.__cause__)


def test_brep_tessellation_reports_missing_face_triangulation(monkeypatch):
    from compas_occ.brep import brep as brep_module

    class ToolWithoutFaceTriangulation:
        @staticmethod
        def Triangulation(*args):
            return None

    monkeypatch.setattr(brep_module.BRep, "BRep_Tool", ToolWithoutFaceTriangulation)

    with pytest.raises(BrepTessellationError, match="no triangulation for BRep face 0") as caught:
        OCCBrep.from_box(Box(1)).to_tessellation(linear_deflection=0.01, angular_deflection=12.0)

    assert caught.value.__cause__ is None


def test_brep_tessellation_wraps_native_face_triangulation_failure(monkeypatch):
    from compas_occ.brep import brep as brep_module

    class ToolWithFailingTriangulation:
        @staticmethod
        def Triangulation(*args):
            raise RuntimeError("Standard_Failure: triangulation lookup failed")

    monkeypatch.setattr(brep_module.BRep, "BRep_Tool", ToolWithFailingTriangulation)

    with pytest.raises(BrepTessellationError, match="could not retrieve triangulation for BRep face 0") as caught:
        OCCBrep.from_box(Box(1)).to_tessellation(linear_deflection=0.01, angular_deflection=12.0)

    assert isinstance(caught.value.__cause__, RuntimeError)
    assert "Standard_Failure" in str(caught.value.__cause__)


def test_brep_polygonal_conversion_is_explicit_result_conversion():
    brep = OCCBrep.from_box(Box(1))
    tessellation = brep.to_tessellation(linear_deflection=0.01, angular_deflection=12.0)
    polygonal = tessellation.to_polygonal_surface()
    assert len(polygonal.vertices) == 24
    assert len(polygonal.faces) == 12


def test_brep_has_no_removed_tessellation_aliases():
    brep = OCCBrep.from_box(Box(1))

    for name in (
        "tessellate",
        "polygonize",
        "to_polygonal_surface",
        "tessellation",
        "compute_tessellation",
        "to_tesselation",
        "to_viewmesh",
        "tessellation_capabilities",
    ):
        assert not hasattr(brep, name)


def test_brep_face_tessellates_through_stable_single_face_brep():
    face = OCCBrep.from_box(Box(1)).faces[0]
    tessellation = face.to_tessellation()

    assert tessellation.number_of_triangles == 2
    assert not hasattr(face, "tessellate")
    assert not hasattr(face, "polygonize")
    assert not hasattr(face, "to_polygonal_surface")


def test_brep_from_iges_accepts_shape_sequences(tmp_path):
    filepath = tmp_path / "multiple.iges"
    write_iges(filepath, [OCCBrep.from_box(Box(1)), OCCBrep.from_sphere(Sphere(0.5))])

    brep = OCCBrep.from_iges(filepath, solid=False)

    assert brep.occ_shape.ShapeType() >= 0
    assert brep.faces


def test_iges_roundtrip_preserves_multiple_geometries(tmp_path):
    filepath = tmp_path / "multiple.iges"
    geometries = [OCCBrep.from_box(Box(1)), OCCBrep.from_sphere(Sphere(0.5))]

    write_iges(filepath, geometries)
    document = read_iges(filepath)

    assert len(document.geometries) == 2
    assert sorted(len(geometry.faces) for geometry in document.geometries) == [1, 6]

    compound = OCCBrep.from_iges(filepath, solid=False)
    assert len(compound.faces) == 7


def test_iges_writer_validates_document_and_mode(tmp_path):
    with pytest.raises(ValueError):
        write_iges(tmp_path / "empty.iges", [])

    with pytest.raises(ValueError):
        write_iges(tmp_path / "invalid-mode.iges", [OCCBrep.from_box(Box(1))], mode=2)


def test_brep_file_roundtrip_preserves_multiple_geometries(tmp_path):
    filepath = tmp_path / "multiple.brep"
    geometries = [OCCBrep.from_box(Box(1)), OCCBrep.from_sphere(Sphere(0.5))]

    write_brep(filepath, geometries)
    document = read_brep(filepath)

    assert len(document.geometries) == 2
    assert all(geometry.is_solid for geometry in document.geometries)

    compound = OCCBrep.from_brep(filepath)
    assert len(compound.solids) == 2


def test_brep_writer_rejects_empty_documents(tmp_path):
    with pytest.raises(ValueError):
        write_brep(tmp_path / "empty.brep", [])


def test_step_roundtrip_preserves_multiple_geometries(tmp_path):
    filepath = tmp_path / "multiple.step"
    geometries = [OCCBrep.from_box(Box(1)), OCCBrep.from_sphere(Sphere(0.5))]

    write_step(filepath, geometries, author="COMPAS", name="Multiple geometries", description="STEP roundtrip", organization="compas.dev")
    document = read_step(filepath)

    assert len(document.geometries) == 2
    assert all(geometry.occ_shape.ShapeType() >= 0 for geometry in document.geometries)

    compound = OCCBrep.from_step(filepath)
    assert len(compound.faces) == sum(len(geometry.faces) for geometry in document.geometries)


def test_step_roundtrip_accepts_mixed_occ_geometries(tmp_path):
    filepath = tmp_path / "mixed.step"
    curve = OCCNurbsCurve.from_line(Line(Point(0, 0, 0), Point(1, 0, 0)))
    brep = OCCBrep.from_box(Box(1))

    write_step(filepath, [curve, brep])
    document = read_step(filepath)

    assert len(document.geometries) == 2
    assert sorted(len(geometry.faces) for geometry in document.geometries) == [0, 6]
    assert any(len(geometry.edges) == 1 for geometry in document.geometries)


def test_extrusion_can_be_capped():
    curve = OCCNurbsCurve.from_circle(Circle(radius=1.0))
    profile = OCCBrepEdge.from_curve(curve)

    brep = OCCBrep.from_extrusion(profile, Vector(0, 0, 2), cap_ends=True)

    assert brep.is_solid
    assert len(brep.faces) == 3


def test_extrusion_can_be_left_uncapped():
    curve = OCCNurbsCurve.from_circle(Circle(radius=1.0))
    profile = OCCBrepEdge.from_curve(curve)

    brep = OCCBrep.from_extrusion(profile, Vector(0, 0, 2), cap_ends=False)

    assert not brep.is_solid
    assert len(brep.faces) == 1


def test_extrusion_accepts_stable_compas_curve():
    occ_curve = OCCNurbsCurve.from_circle(Circle(radius=1.0))
    curve = NurbsCurve(native_curve=occ_curve.native_curve)

    brep = OCCBrep.from_extrusion(curve, Vector(0, 0, 2), cap_ends=True)

    assert brep.is_solid
    assert len(brep.faces) == 3


def test_face_extrusion_can_be_left_uncapped():
    profile = OCCBrepFace.from_polygon(Polygon([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]))

    brep = OCCBrep.from_extrusion(profile, Vector(0, 0, 2), cap_ends=False)

    assert not brep.is_solid
    assert len(brep.faces) == 4


def test_edge_from_stable_curve_embedded_on_surface():
    points = [
        [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
        [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
        [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
        [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
    ]
    surface = NurbsSurface.from_points(points=points)
    circle = Circle(0.5, frame=Frame(Point(1.5, 1.5, 1.5), Vector(1, 0, 0), Vector(0, 1, 0)))
    curve = NurbsCurve.from_circle(circle)

    loop = OCCBrepLoop.from_curves_and_surface([curve], surface)
    face = OCCBrepFace.from_surface(surface)
    face.add_loop(loop)

    assert loop.is_valid
    assert face.is_valid
    assert len(face.loops) == 2


def test_brep_loop_fix_loads_wire_before_performing():
    loop = OCCBrepLoop.from_polygon(Polygon([(0, 0, 0), (2, 0, 0), (2, 1, 0), (0, 1, 0)]))

    loop.fix()

    assert loop.is_valid
    assert len(loop.edges) == 4
    assert len(loop.vertices) == 4


def test_inner_loop_orientation_is_selected_automatically():
    hole = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(Circle(1.0))])
    face = OCCBrepFace.from_plane(Plane.worldXY(), domain_u=(-5, 5), domain_v=(-5, 5))

    face.add_loop(hole)

    assert face.is_valid
    assert face.area == pytest.approx(100 - 3.141592653589793)
    assert face.loops[0].is_same(face.outerloop)
    assert len(face.innerloops) == 1


def test_inner_loops_can_be_added_during_face_construction():
    holes = [
        OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(Circle(1.0, frame=Frame([-2, 0, 0])))]),
        OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(Circle(0.5, frame=Frame([2, 0, 0])))]),
    ]

    face = OCCBrepFace.from_plane(Plane.worldXY(), domain_u=(-5, 5), domain_v=(-5, 5), holes=holes)

    assert face.is_valid
    assert len(face.loops) == 3
    assert face.area == pytest.approx(100 - 1.25 * 3.141592653589793)


def test_invalid_inner_loop_does_not_modify_face():
    face = OCCBrepFace.from_plane(Plane.worldXY(), domain_u=(-5, 5), domain_v=(-5, 5))
    original = face.occ_face
    off_surface = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(Circle(1.0, frame=Frame([0, 0, 2])))])

    with pytest.raises(ValueError):
        face.add_loop(off_surface)

    assert face.occ_face.IsSame(original)
    assert face.is_valid
    assert len(face.loops) == 1


def test_face_boundary_options_are_unambiguous():
    boundary = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(Circle(1.0))])

    with pytest.raises(ValueError):
        OCCBrepFace.from_plane(Plane.worldXY(), domain_u=(-1, 1))

    with pytest.raises(ValueError):
        OCCBrepFace.from_plane(Plane.worldXY(), domain_u=(-1, 1), domain_v=(-1, 1), loop=boundary)

    with pytest.raises(ValueError):
        OCCBrepFace.from_plane(Plane.worldXY(), loop=boundary, boundary=boundary)


def test_face_can_be_constructed_with_boundary_and_holes():
    boundary = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(Circle(2.0))])
    hole = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(Circle(0.5))])

    face = OCCBrepFace.from_plane(Plane.worldXY(), boundary=boundary, holes=[hole])

    assert face.is_valid
    assert len(face.loops) == 2
    assert face.area == pytest.approx(3.75 * 3.141592653589793)

    tessellation = face.to_tessellation(linear_deflection=0.01, angular_deflection=12.0)
    triangulated_area = sum(area_triangle([tessellation.vertices[index] for index in triangle]) for triangle in tessellation.triangles)

    assert triangulated_area == pytest.approx(face.area, rel=0.02)
    assert len(tessellation.polylines) == 2


def test_serialized_face_rebuild_preserves_boundary_roles():
    from compas_occ.brep.builder import OCCBrepBuilder

    boundary = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(Circle(2.0))])
    hole = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(Circle(0.5))])
    face = OCCBrepFace.from_plane(Plane.worldXY(), boundary=boundary, holes=[hole])

    brep = OCCBrepBuilder(make_solid=False).build([face.__data__])
    rebuilt = brep.faces[0]

    assert rebuilt.is_valid
    assert rebuilt.loops[0].is_same(rebuilt.outerloop)
    assert len(rebuilt.innerloops) == 1
    assert rebuilt.area == pytest.approx(face.area)
