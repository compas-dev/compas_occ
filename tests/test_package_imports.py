from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def test_brep_package_imports_in_fresh_interpreter(tmp_path: Path) -> None:
    script = """
import compas_occ.brep as brep
from compas.geometry import Box
from compas.geometry import Brep
from compas_occ.brep import OCCBrep
from compas_occ.brep import OCCBrepEdge
from compas_occ.brep import OCCBrepFace
from compas_occ.brep import OCCBrepLoop
from compas_occ.brep import OCCBrepVertex

assert OCCBrep is brep.OCCBrep
assert OCCBrepEdge is brep.OCCBrepEdge
assert OCCBrepFace is brep.OCCBrepFace
assert OCCBrepLoop is brep.OCCBrepLoop
assert OCCBrepVertex is brep.OCCBrepVertex
assert set(brep.__all__) == {
    "OCCBrep",
    "OCCBrepEdge",
    "OCCBrepFace",
    "OCCBrepLoop",
    "OCCBrepVertex",
}
box = Brep.from_box(Box(1))
assert abs(box.volume - 1.0) < 1e-12
"""

    subprocess.run([sys.executable, "-c", script], check=True, cwd=tmp_path)
