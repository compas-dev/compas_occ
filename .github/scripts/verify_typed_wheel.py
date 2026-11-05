"""Verify that a COMPAS OCC wheel is a usable PEP 561 typed package."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from zipfile import ZipFile

MARKER = "compas_occ/py.typed"
CONSUMER = """from typing import assert_type

from compas_occ.brep import OCCBrep
from compas_occ.geometry import OCCNurbsCurve
from compas_occ.geometry import OCCNurbsSurface


def consume(brep: OCCBrep, curve: OCCNurbsCurve, surface: OCCNurbsSurface) -> None:
    assert_type(brep.area, float)
    assert_type(curve.degree, int)
    assert_type(surface.degree_u, int)
"""


def environment_python(environment: Path) -> Path:
    """Return the Python executable inside a virtual environment."""
    if sys.platform == "win32":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def verify_consumer(wheel: Path, core_wheel: Path) -> None:
    """Type-check a consumer against wheels installed in an isolated environment."""
    with tempfile.TemporaryDirectory(prefix="compas-occ-typed-wheel-") as directory:
        root = Path(directory)
        environment = root / "environment"
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment_python(environment)
        clean_env = os.environ.copy()
        clean_env.pop("PYTHONPATH", None)

        subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--no-deps",
                str(core_wheel.resolve()),
                str(wheel.resolve()),
            ],
            check=True,
            cwd=root,
            env=clean_env,
        )
        subprocess.run(
            [
                str(python),
                "-c",
                "from pathlib import Path; import compas_occ, sys; assert Path(compas_occ.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())",
            ],
            check=True,
            cwd=root,
            env=clean_env,
        )

        consumer = root / "consumer.py"
        consumer.write_text(CONSUMER, encoding="utf-8")
        config = root / "pyrightconfig.json"
        config.write_text(
            json.dumps(
                {
                    "include": ["consumer.py"],
                    "pythonVersion": "3.12",
                    "typeCheckingMode": "standard",
                }
            ),
            encoding="utf-8",
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pyright",
                "--pythonpath",
                str(python),
                "--project",
                str(config),
            ],
            check=True,
            cwd=root,
            env=clean_env,
        )


def verify_wheel(
    wheel: Path,
    *,
    check_consumer: bool = False,
    core_wheel: Path | None = None,
) -> None:
    """Verify typed-package metadata and optionally type-check a consumer."""
    with ZipFile(wheel) as archive:
        names = set(archive.namelist())
        if MARKER not in names:
            raise SystemExit(f"{wheel} is missing {MARKER}")

    if check_consumer:
        if core_wheel is None:
            raise SystemExit("--core-wheel is required with --check-consumer")
        verify_consumer(wheel, core_wheel)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheels", nargs="+", type=Path)
    parser.add_argument("--check-consumer", action="store_true")
    parser.add_argument("--core-wheel", type=Path)
    args = parser.parse_args()

    for wheel in args.wheels:
        verify_wheel(
            wheel,
            check_consumer=args.check_consumer,
            core_wheel=args.core_wheel,
        )


if __name__ == "__main__":
    main()
