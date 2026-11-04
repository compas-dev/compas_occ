import json
import subprocess
import sys
from pathlib import Path

from OCC.Core.Geom2d import Geom2d_Line
from OCC.Core.gp import gp_Ax2d
from OCC.Core.gp import gp_Dir2d
from OCC.Core.gp import gp_Pnt2d

from compas.geometry import Frame
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Vector
from compas_occ.geometry import OCCCurve2d
from compas_occ.geometry import OCCNurbsCurve


ROOT = Path(__file__).parents[1]


def test_curve_typing_fixture_has_no_diagnostics():
    fixture = ROOT / "tests" / "typing" / "curve_substitutability.py"
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


def test_occ_curve_implements_updated_curve_contract():
    curve = OCCNurbsCurve.from_line(Line([0, 0, 0], [2, 0, 0]))

    polyline = curve.to_polyline(n=4, domain=(0.25, 0.75))

    assert len(polyline.points) == 5
    assert polyline.start.distance_to_point(Point(0.5, 0, 0)) < 1e-12
    assert polyline.end.distance_to_point(Point(1.5, 0, 0)) < 1e-12
    assert curve.length == 2.0
    assert curve.closest_point([0.5, 1.0, 0.0]).distance_to_point(Point(0.5, 0, 0)) < 1e-12

    spatial_curve = OCCNurbsCurve.from_line(Line([0, 0, 0], [2, 1, 1]))
    assert spatial_curve.aabb.xsize == 2.0


class CustomNurbsCurve(OCCNurbsCurve):
    pass


def test_occ_curve_copy_supports_data_contract():
    curve = OCCNurbsCurve.from_line(Line([0, 0, 0], [2, 0, 0]))
    curve.name = "source"

    copy = curve.copy()
    typed_copy = curve.copy(cls=CustomNurbsCurve)
    guid_copy = curve.copy(copy_guid=True)

    assert copy is not curve
    assert copy.name == curve.name
    assert copy.guid != curve.guid

    assert type(typed_copy) is CustomNurbsCurve
    assert typed_copy.name == curve.name
    assert typed_copy.guid != curve.guid

    assert guid_copy.name == curve.name
    assert guid_copy.guid == curve.guid


def test_occ_curve_point_and_tangent_support_local_frame_coordinates():
    curve = OCCNurbsCurve.from_line(Line([10, 20, 30], [10, 22, 30]))
    curve.frame = Frame([10, 20, 30], [0, 1, 0], [-1, 0, 0])

    assert curve.point_at(0.5).distance_to_point(Point(10, 21, 30)) < 1e-12
    assert curve.point_at(0.5, world=False).distance_to_point(Point(1, 0, 0)) < 1e-12
    assert (curve.tangent_at(0.5) - Vector(0, 2, 0)).length < 1e-12
    assert (curve.tangent_at(0.5, world=False) - Vector(2, 0, 0)).length < 1e-12


def test_occ_curve2d_point_and_tangent_support_local_frame_coordinates():
    native_curve = Geom2d_Line(gp_Ax2d(gp_Pnt2d(10, 20), gp_Dir2d(0, 1)))
    curve = OCCCurve2d(native_curve)
    curve.frame = Frame([10, 20, 0], [0, 1, 0], [-1, 0, 0])

    assert curve.point_at(1.0).distance_to_point(Point(10, 21, 0)) < 1e-12
    assert curve.point_at(1.0, world=False).distance_to_point(Point(1, 0, 0)) < 1e-12
    assert (curve.tangent_at(1.0) - Vector(0, 1, 0)).length < 1e-12
    assert (curve.tangent_at(1.0, world=False) - Vector(1, 0, 0)).length < 1e-12
