import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

from compas.geometry import Brep
from compas.geometry import Point
from compas_occ.geometry import OCCNurbsSurface


ROOT = Path(__file__).parents[1]
SURFACE_FACTORY_NAMES = [
    "from_interpolation",
    "from_native",
    "from_parameters",
    "from_plane",
    "from_points",
]
SURFACE_OPERATION_NAMES = [
    "from_extrusion",
    "from_fill",
    "from_frame",
    "from_step",
    "surface_points",
    "surface_weights",
    "surface_knots_u",
    "surface_knots_v",
    "surface_mults_u",
    "surface_mults_v",
    "surface_degree_u",
    "surface_degree_v",
    "surface_domain_u",
    "surface_domain_v",
    "surface_is_periodic_u",
    "surface_is_periodic_v",
    "surface_isocurve_u",
    "surface_isocurve_v",
    "surface_boundary",
    "surface_point_at",
    "surface_normal_at",
    "surface_frame_at",
    "surface_closest_point",
    "surface_transform",
    "surface_to_brep",
    "surface_to_step",
]


def _assert_signatures_match(plugin, pluggable):
    plugin_signature = inspect.signature(plugin)
    core_signature = inspect.signature(pluggable)

    assert tuple(plugin_signature.parameters) == tuple(core_signature.parameters)
    for plugin_parameter, core_parameter in zip(plugin_signature.parameters.values(), core_signature.parameters.values()):
        assert plugin_parameter.kind == core_parameter.kind
        assert plugin_parameter.default == core_parameter.default
        assert plugin_parameter.annotation == core_parameter.annotation
    assert plugin_signature.return_annotation == core_signature.return_annotation


def test_surface_from_native_plugin_signature_matches_core_pluggable():
    from compas.geometry.surfaces.surface import surface_from_native as core_surface_from_native
    from compas_occ.plugins.surfaces import surface_from_native as occ_surface_from_native

    _assert_signatures_match(occ_surface_from_native, core_surface_from_native)


@pytest.mark.parametrize("name", SURFACE_FACTORY_NAMES)
def test_nurbssurface_factory_plugin_signature_matches_core_pluggable(name):
    from compas.geometry.surfaces import nurbs_operations as core_surfaces
    from compas_occ.plugins import surfaces as occ_surfaces

    _assert_signatures_match(getattr(occ_surfaces, name), getattr(core_surfaces, name))


@pytest.mark.parametrize("name", SURFACE_OPERATION_NAMES)
def test_nurbssurface_operation_plugin_signature_matches_core_pluggable(name):
    from compas.geometry.surfaces import nurbs_operations as core_surfaces
    from compas_occ.plugins import surfaces as occ_surfaces

    _assert_signatures_match(getattr(occ_surfaces, name), getattr(core_surfaces, name))


def test_surface_factory_plugin_typing_fixture_has_no_diagnostics():
    fixture = ROOT / "tests" / "typing" / "surface_plugins_wp3.py"
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


def test_surface_factories_forward_defaults_and_arguments(monkeypatch):
    from compas_occ.plugins import surfaces

    calls = []

    def capture(method, *args, **kwargs):
        calls.append((method, args, kwargs))
        return object()

    monkeypatch.setattr(surfaces, "_new", capture)
    points = [[(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)], [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0)]]

    surfaces.from_interpolation(points)
    surfaces.from_points(points)
    surfaces.from_parameters(points, [[1.0, 1.0], [1.0, 1.0]], [0.0, 1.0], [0.0, 1.0], [2, 2], [2, 2], 1, 1)

    assert calls == [
        ("from_interpolation", (points,), {"precision": 1e-3}),
        ("from_points", (points,), {"degree_u": 3, "degree_v": 3}),
        (
            "from_parameters",
            (points, [[1.0, 1.0], [1.0, 1.0]], [0.0, 1.0], [0.0, 1.0], [2, 2], [2, 2], 1, 1),
            {"is_periodic_u": False, "is_periodic_v": False},
        ),
    ]


def test_surface_transform_accepts_a_raw_transformation_matrix():
    from compas_occ.plugins.surfaces import surface_transform

    surface = OCCNurbsSurface.from_points(
        [
            [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
        ],
        degree_u=1,
        degree_v=1,
    )

    surface_transform(
        surface,
        [
            [1.0, 0.0, 0.0, 2.0],
            [0.0, 1.0, 0.0, 3.0],
            [0.0, 0.0, 1.0, 4.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
    )

    assert surface.point_at(0.0, 0.0) == Point(2.0, 3.0, 4.0)


def test_surface_to_brep_returns_the_core_wrapper():
    from compas_occ.plugins.surfaces import surface_to_brep

    surface = OCCNurbsSurface.from_points(
        [
            [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
        ],
        degree_u=1,
        degree_v=1,
    )

    brep = surface_to_brep(surface)

    assert type(brep) is Brep
    assert brep.native_brep is not None


def test_stable_surface_facade_dispatches_matrix_transform_and_brep_conversion():
    from compas.geometry import NurbsSurface

    surface = NurbsSurface.from_points(
        [
            [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
        ],
        degree_u=1,
        degree_v=1,
    )

    surface.transform(
        [
            [1.0, 0.0, 0.0, 2.0],
            [0.0, 1.0, 0.0, 3.0],
            [0.0, 0.0, 1.0, 4.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    brep = surface.to_brep()

    assert surface.point_at(0.0, 0.0) == Point(2.0, 3.0, 4.0)
    assert type(brep) is Brep
    assert brep.native_brep is not None


def test_stable_surface_facade_rejects_unsupported_affine_without_mutation():
    from compas.geometry import NurbsSurface

    surface = NurbsSurface.from_points(
        [
            [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
        ],
        degree_u=1,
        degree_v=1,
    )
    point = surface.point_at(0.0, 0.0)

    with pytest.raises(ValueError, match="gp_Trsf cannot represent"):
        surface.transform(
            [
                [2.0, 0.0, 0.0, 0.0],
                [0.0, 3.0, 0.0, 0.0],
                [0.0, 0.0, 4.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

    assert surface.point_at(0.0, 0.0) == point
