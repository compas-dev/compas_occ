import pytest
from OCC.Core.Geom import Geom_SphericalSurface

from compas.geometry import Box
from compas.geometry import Circle
from compas.geometry import Frame
from compas.geometry import IntersectionResult
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Sphere
from compas.geometry import intersection_curve_brep as plugin_intersection_curve_brep
from compas.geometry import intersection_curve_surface as plugin_intersection_curve_surface
from compas.geometry import intersection_line_brep as plugin_intersection_line_brep
from compas.geometry import intersection_line_surface as plugin_intersection_line_surface
from compas.geometry import intersection_plane_brep as plugin_intersection_plane_brep
from compas.geometry import intersection_plane_surface as plugin_intersection_plane_surface
from compas.geometry import intersection_surface_brep as plugin_intersection_surface_brep
from compas.geometry import intersection_surface_surface as plugin_intersection_surface_surface
from compas_occ.brep import OCCBrep
from compas_occ.conversions import sphere_to_occ
from compas_occ.geometry import OCCNurbsSurface
from compas_occ.geometry import OCCSurface
from compas_occ.intersections import intersection_curve_brep
from compas_occ.intersections import intersection_curve_surface
from compas_occ.intersections import intersection_line_brep
from compas_occ.intersections import intersection_line_surface
from compas_occ.intersections import intersection_plane_brep
from compas_occ.intersections import intersection_plane_surface
from compas_occ.intersections import intersection_surface_brep
from compas_occ.intersections import intersection_surface_surface


@pytest.fixture
def plane_surface():
    return OCCNurbsSurface.from_plane(Plane.worldXY())


@pytest.fixture
def box_brep():
    return OCCBrep.from_box(Box(2))


def test_intersection_line_surface_returns_points(plane_surface):
    result = intersection_line_surface(Line([0.5, -0.5, -1], [0.5, -0.5, 1]), plane_surface)

    assert isinstance(result, IntersectionResult)
    assert result.is_single
    assert result[0] == Point(0.5, -0.5, 0)


def test_intersection_line_surface_can_be_empty(plane_surface):
    result = intersection_line_surface(Line([0, 0, 1], [1, 0, 1]), plane_surface)

    assert result.is_empty


def test_intersection_curve_surface_returns_points(plane_surface):
    curve = NurbsCurve.from_line(Line([0.5, -0.5, -1], [0.5, -0.5, 1]))

    result = intersection_curve_surface(curve, plane_surface)

    assert result.is_single
    assert result[0] == Point(0.5, -0.5, 0)


def test_intersection_plane_surface_returns_curves(plane_surface):
    result = intersection_plane_surface(Plane([0.5, 0, 0], [1, 0, 0]), plane_surface)

    assert result
    assert all(not isinstance(item, Point) for item in result)


def test_intersection_surface_surface_returns_curves():
    first = OCCSurface(Geom_SphericalSurface(sphere_to_occ(Sphere(1))))
    second = OCCSurface(Geom_SphericalSurface(sphere_to_occ(Sphere(1, frame=Frame([1, 0, 0])))))

    result = intersection_surface_surface(first, second)

    assert result
    assert all(isinstance(item, Circle) for item in result)


def test_intersection_line_brep_returns_unique_boundary_points(box_brep):
    result = intersection_line_brep(Line([0, 0, -2], [0, 0, 2]), box_brep)

    assert len(result) == 2
    assert sorted(point.z for point in result) == pytest.approx([-1, 1])


def test_intersection_curve_brep_returns_unique_boundary_points(box_brep):
    curve = NurbsCurve.from_line(Line([0, 0, -2], [0, 0, 2]))

    result = intersection_curve_brep(curve, box_brep)

    assert len(result) == 2
    assert sorted(point.z for point in result) == pytest.approx([-1, 1])


def test_intersection_plane_brep_returns_section_curves(box_brep):
    result = intersection_plane_brep(Plane.worldXY(), box_brep)

    assert len(result) == 4


def test_intersection_surface_brep_returns_section_curves(box_brep, plane_surface):
    result = intersection_surface_brep(plane_surface, box_brep)

    assert result


def test_compas_pluggables_dispatch_to_occ_plugins(box_brep, plane_surface):
    line = Line([0, 0, -2], [0, 0, 2])
    curve = NurbsCurve.from_line(line)
    sphere_a = OCCSurface(Geom_SphericalSurface(sphere_to_occ(Sphere(1))))
    sphere_b = OCCSurface(Geom_SphericalSurface(sphere_to_occ(Sphere(1, frame=Frame([1, 0, 0])))))

    assert plugin_intersection_line_surface(line, plane_surface)
    assert plugin_intersection_plane_surface(Plane([0.5, 0, 0], [1, 0, 0]), plane_surface)
    assert plugin_intersection_curve_surface(curve, plane_surface)
    assert plugin_intersection_surface_surface(sphere_a, sphere_b)
    assert len(plugin_intersection_line_brep(line, box_brep)) == 2
    assert plugin_intersection_plane_brep(Plane.worldXY(), box_brep)
    assert len(plugin_intersection_curve_brep(curve, box_brep)) == 2
    assert plugin_intersection_surface_brep(plane_surface, box_brep)


@pytest.mark.parametrize(
    "function,args",
    [
        (intersection_curve_surface, (object(), object())),
        (intersection_surface_surface, (object(), object())),
        (intersection_curve_brep, (object(), object())),
        (intersection_surface_brep, (object(), object())),
    ],
)
def test_intersections_reject_objects_without_native_geometry(function, args):
    with pytest.raises(TypeError):
        function(*args)
