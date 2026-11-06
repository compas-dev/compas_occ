from __future__ import annotations

from contextlib import nullcontext
import importlib.util
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile

import pytest


SCRIPT = Path(__file__).parents[1] / ".github" / "scripts" / "verify_typed_wheel.py"
SPEC = importlib.util.spec_from_file_location("verify_typed_wheel", SCRIPT)
assert SPEC
assert SPEC.loader
verify_typed_wheel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_typed_wheel)


def prepare_consumer_environment(monkeypatch, tmp_path: Path) -> list[Path]:
    """Replace environment creation with an inspectable temporary layout."""
    monkeypatch.setattr(
        verify_typed_wheel.tempfile,
        "TemporaryDirectory",
        lambda **kwargs: nullcontext(str(tmp_path)),
    )
    created = []

    class EnvironmentBuilder:
        def __init__(self, *, with_pip: bool) -> None:
            assert with_pip

        def create(self, environment: Path) -> None:
            created.append(environment)
            verify_typed_wheel.environment_python(environment).parent.mkdir(parents=True)

    monkeypatch.setattr(verify_typed_wheel.venv, "EnvBuilder", EnvironmentBuilder)
    return created


def make_wheel(tmp_path: Path, *, include_marker: bool = True) -> Path:
    wheel = tmp_path / "compas_occ-1.5.0-py3-none-any.whl"
    with ZipFile(wheel, "w") as archive:
        archive.writestr("compas_occ/__init__.py", "")
        if include_marker:
            archive.writestr("compas_occ/py.typed", "")
    return wheel


def test_source_package_has_typed_marker() -> None:
    package = Path(__file__).parents[1] / "src" / "compas_occ"

    assert (package / "py.typed").is_file()


def test_typed_wheel_is_accepted(tmp_path: Path) -> None:
    verify_typed_wheel.verify_wheel(make_wheel(tmp_path))


def test_wheel_without_typed_marker_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="compas_occ/py.typed"):
        verify_typed_wheel.verify_wheel(make_wheel(tmp_path, include_marker=False))


def test_consumer_check_requires_core_wheel(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="--core-wheel"):
        verify_typed_wheel.verify_wheel(make_wheel(tmp_path), check_consumer=True)


def test_consumer_checks_public_result_types() -> None:
    source = verify_typed_wheel.CONSUMER

    assert "assert_type(brep.to_tessellation" in source
    assert "assert_type(occ_brep.to_tessellation" in source
    assert "assert_type(occ_brep.area, float)" in source
    assert "assert_type(curve.degree, int)" in source
    assert "assert_type(surface.degree_u, int)" in source


def test_consumer_check_uses_isolated_environment(monkeypatch, tmp_path: Path) -> None:
    created = prepare_consumer_environment(monkeypatch, tmp_path)
    monkeypatch.setenv("PYTHONPATH", "/checkout/src")
    calls = []
    monkeypatch.setattr(
        verify_typed_wheel.subprocess,
        "run",
        lambda command, **kwargs: calls.append((command, kwargs)),
    )
    wheel = tmp_path / "dist" / "compas_occ.whl"
    core_wheel = tmp_path / "core" / "compas.whl"

    verify_typed_wheel.verify_consumer(wheel, core_wheel)

    environment = tmp_path / "environment"
    python = verify_typed_wheel.environment_python(environment)
    assert created == [environment]
    assert calls[0][0] == [
        str(python),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-deps",
        str(core_wheel.resolve()),
        str(wheel.resolve()),
    ]
    assert calls[0][1]["check"] is True
    assert calls[0][1]["cwd"] == tmp_path
    assert "PYTHONPATH" not in calls[0][1]["env"]
    assert calls[1][0][:3] == [str(python), "-c", calls[1][0][2]]
    assert "compas_occ.__file__" in calls[1][0][2]
    assert "sys.prefix" in calls[1][0][2]
    assert calls[1][1]["cwd"] == tmp_path
    assert calls[2][0] == [
        verify_typed_wheel.sys.executable,
        "-m",
        "pyright",
        "--pythonpath",
        str(python),
        "--project",
        str(tmp_path / "pyrightconfig.json"),
    ]
    assert calls[2][1]["check"] is True
    assert calls[2][1]["cwd"] == tmp_path
    assert json.loads((tmp_path / "pyrightconfig.json").read_text(encoding="utf-8")) == {
        "include": ["consumer.py"],
        "pythonVersion": "3.12",
        "typeCheckingMode": "standard",
    }
    assert (tmp_path / "consumer.py").read_text(encoding="utf-8") == verify_typed_wheel.CONSUMER


def test_consumer_check_propagates_pyright_failure(monkeypatch, tmp_path: Path) -> None:
    prepare_consumer_environment(monkeypatch, tmp_path)

    def run(command, **kwargs):
        if "pyright" in command:
            raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(verify_typed_wheel.subprocess, "run", run)

    with pytest.raises(subprocess.CalledProcessError):
        verify_typed_wheel.verify_consumer(tmp_path / "compas_occ.whl", tmp_path / "compas.whl")
