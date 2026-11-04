import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
SURFACE_FACTORY_NAMES = [
    "from_interpolation",
    "from_native",
    "from_parameters",
    "from_plane",
    "from_points",
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
