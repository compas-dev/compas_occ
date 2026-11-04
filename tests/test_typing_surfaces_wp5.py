import json
import subprocess
import sys
from pathlib import Path

from compas.geometry import Box
from compas.geometry import Point
from compas.geometry import Surface
from compas_occ.geometry import OCCNurbsSurface
from compas_occ.geometry import OCCSurface


ROOT = Path(__file__).parents[1]


def test_surface_typing_fixture_has_no_diagnostics():
    fixture = ROOT / "tests" / "typing" / "surface_contracts_wp5.py"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pyright",
            "--outputjson",
            "--pythonpath",
            sys.executable,
            str(fixture),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode in {0, 1}, result.stderr
    assert json.loads(result.stdout)["generalDiagnostics"] == []


def test_occ_surface_matches_base_runtime_contract():
    surface: Surface = OCCNurbsSurface.from_points(
        [
            [[0, 0, 0], [1, 0, 1]],
            [[0, 1, 0], [1, 1, 0]],
        ],
        degree_u=1,
        degree_v=1,
    )

    assert isinstance(surface.aabb, Box)
    assert isinstance(surface.obb, Box)

    plane: Surface = OCCNurbsSurface.from_points(
        [
            [[0, 0, 0], [1, 0, 0]],
            [[0, 1, 0], [1, 1, 0]],
        ],
        degree_u=1,
        degree_v=1,
    )
    assert plane.closest_point([0.25, 0.5, 1.0]) == Point(0.25, 0.5, 0.0)
    projection = plane.closest_point([0.25, 0.5, 1.0], return_parameters=True)
    assert projection is not None
    point, parameters = projection
    assert point == Point(0.25, 0.5, 0.0)
    assert parameters == (0.25, 0.5)

    surface.name = "Named surface"
    copied = surface.copy()
    assert copied is not surface
    assert type(copied) is OCCNurbsSurface
    assert copied.name == surface.name
    assert copied.guid != surface.guid
    assert copied.native_surface is not surface.native_surface

    copied_with_guid = surface.copy(copy_guid=True)
    assert copied_with_guid.name == surface.name
    assert copied_with_guid.guid == surface.guid

    copied_as_surface = surface.copy(cls=OCCSurface)
    assert type(copied_as_surface) is OCCSurface
    assert copied_as_surface.name == surface.name
    assert copied_as_surface.guid != surface.guid
    assert copied_as_surface.native_surface is not surface.native_surface

    copied_as_surface_with_guid = surface.copy(cls=OCCSurface, copy_guid=True)
    assert type(copied_as_surface_with_guid) is OCCSurface
    assert copied_as_surface_with_guid.name == surface.name
    assert copied_as_surface_with_guid.guid == surface.guid


def test_occ_nurbs_control_point_access_contract():
    surface = OCCNurbsSurface.from_points(
        [
            [[0, 0, 0], [1, 0, 0]],
            [[0, 1, 0], [1, 1, 0]],
        ],
        degree_u=1,
        degree_v=1,
    )

    assert surface.points[0] == [Point(0, 0, 0), Point(1, 0, 0)]
    assert surface.points[1, 0] == Point(1, 0, 0)
    assert list(surface.points) == surface.points.points
