from pathlib import Path

from compas_viewer import Viewer

from compas.geometry import Box
from compas.geometry import Cylinder
from compas.geometry import Frame
from compas_occ.brep import OCCBrep

IGES = Path(__file__).parent / "booleans.iges"
STEP = Path(__file__).parent / "booleans.step"

# =============================================================================
# Construct boolean Brep
# =============================================================================

R = 1.4
YZ = Frame.worldYZ()
ZX = Frame.worldZX()
XY = Frame.worldXY()

box = OCCBrep.from_box(Box(2 * R))
cx = OCCBrep.from_cylinder(Cylinder(0.7 * R, 4 * R, frame=YZ))
cy = OCCBrep.from_cylinder(Cylinder(0.7 * R, 4 * R, frame=ZX))
cz = OCCBrep.from_cylinder(Cylinder(0.7 * R, 4 * R, frame=XY))

brep = box.boolean_union(cx, cy, cz)

# =============================================================================
# Write/Read to IGES
# =============================================================================

brep.to_iges(IGES)
brep = OCCBrep.from_iges(IGES)

# =============================================================================
# Write/Read to STEP
# =============================================================================

brep.to_step(STEP)
brep = OCCBrep.from_step(STEP)

# =============================================================================
# Visualisation
# =============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [4, -6, 2]

viewer.scene.add(brep, linewidth=2, show_points=False)

viewer.show()
