from pathlib import Path

from compas_viewer import Viewer

from compas.geometry import Box
from compas.geometry import Brep
from compas.geometry import Cylinder
from compas.geometry import Frame

filepath = Path(__file__).parent / "booleans.iges"

# =============================================================================
# Construct boolean Brep
# =============================================================================

R = 1.4
YZ = Frame.worldYZ()
ZX = Frame.worldZX()
XY = Frame.worldXY()

box = Box(2 * R).to_brep()
cx = Cylinder(0.7 * R, 4 * R, frame=YZ).to_brep()
cy = Cylinder(0.7 * R, 4 * R, frame=ZX).to_brep()
cz = Cylinder(0.7 * R, 4 * R, frame=XY).to_brep()

result = box - (cx + cy + cz)

# =============================================================================
# Export to IGES
# =============================================================================

result.to_iges(filepath)

# =============================================================================
# Read from IGES
# =============================================================================

brep = Brep.from_iges(filepath)

# =============================================================================
# Visualisation
# =============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [4, -6, 2]

viewer.scene.add(brep, linewidth=2, show_points=False)

viewer.show()
