from pathlib import Path
import compas
from compas.tolerance import TOL
from compas.geometry import NurbsSurface
from compas_occ.geometry import OCCNurbsSurface

here = Path(__file__).parent
filepath = here / "surface_from_rhino.json"


def test_surface_from_rhino():
    surface: OCCNurbsSurface = compas.json_load(filepath)  # type: ignore

    assert isinstance(surface, OCCNurbsSurface)
    assert isinstance(surface, NurbsSurface)

    for u, col in enumerate(surface.points):  # type: ignore
        for v, point in enumerate(col):
            assert point == surface.points[u][v]
            assert TOL.is_close(point[0], u * 18 / 3)
            assert TOL.is_close(point[1], v * 10 / 3)

    after: NurbsSurface = NurbsSurface.from_jsonstring(surface.to_jsonstring())  # type: ignore

    assert isinstance(after, OCCNurbsSurface)
    assert isinstance(after, NurbsSurface)

    for u, col in enumerate(surface.points):  # type: ignore
        for v, point in enumerate(col):
            assert point == after.points[u][v]

    assert surface.degree_u == after.degree_u
    assert surface.degree_v == after.degree_v
    assert surface.knots_u == after.knots_u
    assert surface.knots_v == after.knots_v
    assert surface.weights == after.weights
