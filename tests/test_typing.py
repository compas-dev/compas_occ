import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]
TYPING_FIXTURES = ROOT / "tests" / "typing"


def test_intersection_plugin_typing_fixture_has_no_diagnostics():
    fixture = TYPING_FIXTURES / "intersection_plugins.py"
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
