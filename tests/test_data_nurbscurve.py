from pathlib import Path
import compas
from compas.geometry import NurbsCurve
from compas_occ.geometry import OCCNurbsCurve


here = Path(__file__).parent
filepath = here / "curve_from_rhino.json"


def test_curve_from_rhino():
    curve: OCCNurbsCurve = compas.json_load(filepath)  # type: ignore

    assert isinstance(curve, OCCNurbsCurve)
    assert isinstance(curve, NurbsCurve)

    assert curve.points[0] == [0.0, 0.0, 0.0]
    assert curve.points[1] == [2.0, 10.0, 0.0]
    assert curve.points[2] == [4.0, -3.0, 7.0]
    assert curve.points[3] == [6.0, 10.0, 0.0]
    assert curve.points[4] == [8.0, -3.0, 0.0]
    assert curve.points[-1] == [10.0, 0.0, 0.0]

    after: NurbsCurve = NurbsCurve.from_jsonstring(curve.to_jsonstring())  # type: ignore

    assert isinstance(after, OCCNurbsCurve)
    assert isinstance(after, NurbsCurve)

    for i in range(len(curve.points)):
        assert curve.points[i] == after.points[i]

    assert curve.degree == after.degree
    assert curve.knots == after.knots
    assert curve.weights == after.weights
