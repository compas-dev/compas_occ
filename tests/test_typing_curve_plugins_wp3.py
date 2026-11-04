import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
CURVE_FACTORY_NAMES = ["from_native", "from_interpolation", "from_parameters", "from_points"]


def _assert_signatures_match(plugin, core):
    plugin_signature = inspect.signature(plugin)
    core_signature = inspect.signature(core)

    assert tuple(plugin_signature.parameters) == tuple(core_signature.parameters)
    for plugin_parameter, core_parameter in zip(plugin_signature.parameters.values(), core_signature.parameters.values()):
        assert plugin_parameter.kind == core_parameter.kind
        assert plugin_parameter.default == core_parameter.default
        assert plugin_parameter.annotation == core_parameter.annotation
    assert plugin_signature.return_annotation == core_signature.return_annotation


def test_curve_from_native_plugin_signature_matches_core_pluggable():
    from compas.geometry.curves.curve import curve_from_native as core_curve_from_native
    from compas_occ.plugins.curves import curve_from_native as plugin_curve_from_native

    _assert_signatures_match(plugin_curve_from_native, core_curve_from_native)


@pytest.mark.parametrize("name", CURVE_FACTORY_NAMES)
def test_nurbscurve_factory_plugin_signature_matches_core_pluggable(name):
    from compas.geometry.curves import nurbs_operations
    from compas_occ.plugins import curves

    _assert_signatures_match(getattr(curves, name), getattr(nurbs_operations, name))


def test_curve_factory_plugin_typing_fixture_has_no_diagnostics():
    fixture = ROOT / "tests" / "typing" / "curve_factory_plugins_wp3.py"
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


def test_curve_factories_forward_defaults_and_arguments(monkeypatch):
    from compas_occ.plugins import curves

    calls = []

    def capture(method, *args, **kwargs):
        calls.append((method, args, kwargs))
        return object()

    monkeypatch.setattr(curves, "_new", capture)
    points = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)]

    curves.from_interpolation(points)
    curves.from_points(points)
    curves.from_parameters(points, [1.0, 1.0], [0.0, 1.0], [2, 2], 1)

    assert calls == [
        ("from_interpolation", (points,), {"precision": 1e-3}),
        ("from_points", (points,), {"degree": 3, "is_periodic": False}),
        ("from_parameters", (points, [1.0, 1.0], [0.0, 1.0], [2, 2], 1), {"is_periodic": False}),
    ]
