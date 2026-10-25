from pathlib import Path

import compas
from compas.geometry import Frame
from compas.geometry import NurbsSurface
from compas.geometry import Tessellation
from compas.geometry import Translation
from compas.tolerance import TOL
from compas_occ.geometry import OCCNurbsSurface


HERE = Path(__file__).parent
FILEPATH = HERE / "surface_from_rhino.json"


def test_surface_from_rhino():
    surface: NurbsSurface = compas.json_load(FILEPATH)  # type: ignore

    assert type(surface) is NurbsSurface

    for v, row in enumerate(surface.control_points):
        for u, point in enumerate(row):
            assert point == surface.control_points[v][u]
            assert TOL.is_close(point[0], v * 18 / 3)
            assert TOL.is_close(point[1], u * 10 / 3)

    after: NurbsSurface = NurbsSurface.from_jsonstring(surface.to_jsonstring())  # type: ignore

    assert type(after) is NurbsSurface
    assert surface.control_points == after.control_points
    assert surface.degree_u == after.degree_u
    assert surface.degree_v == after.degree_v
    assert surface.knots_u == after.knots_u
    assert surface.knots_v == after.knots_v
    assert surface.weights == after.weights


def test_surface_operation_plugins():
    surface = NurbsSurface.from_points(
        [
            [[0, 0, 0], [1, 0, 0], [2, 0, 0]],
            [[0, 1, 0], [1, 1, 1], [2, 1, 0]],
            [[0, 2, 0], [1, 2, 0], [2, 2, 0]],
        ],
        degree_u=2,
        degree_v=2,
    )

    assert type(surface) is NurbsSurface
    assert surface.degree_u == 2
    assert surface.degree_v == 2
    assert len(surface.control_points) == 3
    assert len(surface.control_points[0]) == 3
    assert len(surface.boundary()) == 4

    point = surface.point_at(0.5, 0.5)
    closest, parameters = surface.closest_point(point, return_parameters=True)
    assert closest == point
    assert TOL.is_allclose(parameters, [0.5, 0.5])

    surface.transform(Translation.from_vector([0, 0, 1]))
    assert TOL.is_allclose(surface.point_at(0.5, 0.5), [point.x, point.y, point.z + 1])


def test_occ_surface_is_a_standalone_backend_adapter():
    surface = OCCNurbsSurface.from_points(
        [
            [[0, 0, 0], [1, 0, 0]],
            [[0, 1, 0], [1, 1, 0]],
        ],
        degree_u=1,
        degree_v=1,
    )

    assert type(surface) is OCCNurbsSurface
    assert not isinstance(surface, NurbsSurface)
    assert surface.degree_u == 1
    assert surface.degree_v == 1


def test_occ_surface_uses_compas_tessellation_infrastructure():
    surface = OCCNurbsSurface.from_points(
        [
            [[0, 0, 0], [1, 0, 0]],
            [[0, 1, 0], [1, 1, 0]],
        ],
        degree_u=1,
        degree_v=1,
    )

    tessellation = surface.compute_tessellation(nu=2, nv=3)

    assert isinstance(tessellation, Tessellation)
    assert tessellation.number_of_vertices == 12
    assert tessellation.number_of_triangles == 12
    assert len(tessellation.vertex_normals) == 12
    assert len(tessellation.texture_coordinates) == 12


def test_surface_from_frame_uses_stable_wrapper():
    surface = NurbsSurface.from_frame(Frame.worldXY())

    assert type(surface) is NurbsSurface
    assert surface.degree_u == 1
    assert surface.degree_v == 1
    assert surface.point_at(0.0, 0.0) == [0, 0, 0]
