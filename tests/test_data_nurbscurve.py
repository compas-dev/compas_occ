from pathlib import Path
import compas
from compas.geometry import NurbsCurve
from compas.geometry import Translation
from compas.tolerance import TOL
from compas_occ.geometry import OCCNurbsCurve


here = Path(__file__).parent
filepath = here / "curve_from_rhino.json"


def test_curve_from_rhino():
    curve: NurbsCurve = compas.json_load(filepath)  # type: ignore

    assert type(curve) is NurbsCurve

    assert curve.points[0] == [0.0, 0.0, 0.0]
    assert curve.points[1] == [2.0, 10.0, 0.0]
    assert curve.points[2] == [4.0, -3.0, 7.0]
    assert curve.points[3] == [6.0, 10.0, 0.0]
    assert curve.points[4] == [8.0, -3.0, 0.0]
    assert curve.points[-1] == [10.0, 0.0, 0.0]

    after: NurbsCurve = NurbsCurve.from_jsonstring(curve.to_jsonstring())  # type: ignore

    assert type(after) is NurbsCurve

    for i in range(len(curve.points)):
        assert curve.points[i] == after.points[i]

    assert curve.degree == after.degree
    assert curve.knots == after.knots
    assert curve.weights == after.weights


def test_curve_operation_plugins():
    curve = NurbsCurve.from_points([[0, 0, 0], [1, 1, 0], [2, 0, 0]], degree=2)

    assert type(curve) is NurbsCurve
    assert curve.degree == 2
    assert len(curve.points) == 3
    assert curve.length > 0.0

    start = curve.point_at(curve.domain[0])
    end = curve.point_at(curve.domain[1])
    assert curve.closest_point(start) == start

    parameters, points = curve.divide_by_count(2, return_points=True)
    assert len(parameters) == 3
    assert len(points) == 3

    curve.reverse()
    assert curve.point_at(curve.domain[0]) == end
    assert curve.point_at(curve.domain[1]) == start

    curve.transform(Translation.from_vector([1, 2, 3]))
    transformed_start = curve.point_at(curve.domain[0])
    assert TOL.is_allclose(transformed_start, [end.x + 1, end.y + 2, end.z + 3])


def test_occ_curve_is_a_standalone_backend_adapter():
    curve = OCCNurbsCurve.from_points([[0, 0, 0], [1, 1, 0], [2, 0, 0]], degree=2)

    assert type(curve) is OCCNurbsCurve
    assert not isinstance(curve, NurbsCurve)
    assert curve.degree == 2
    assert len(curve.points) == 3
    assert curve.length() > 0.0


def test_curve_step_roundtrip_uses_stable_wrapper(tmp_path):
    curve = NurbsCurve.from_points([[0, 0, 0], [1, 1, 0], [2, 0, 0]], degree=2)
    filepath = tmp_path / "curve.step"

    curve.to_step(filepath)
    restored = NurbsCurve.from_step(filepath)

    assert type(restored) is NurbsCurve
    assert restored.degree == curve.degree
    assert restored.point_at(restored.domain[0]) == curve.point_at(curve.domain[0])
    assert restored.point_at(restored.domain[1]) == curve.point_at(curve.domain[1])
