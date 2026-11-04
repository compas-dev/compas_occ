import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_brep_component_substitutability_has_no_diagnostics() -> None:
    fixture = ROOT / "tests" / "typing" / "brep_component_substitutability.py"
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
