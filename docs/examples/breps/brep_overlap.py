# type: ignore
from compas.geometry import Box
from compas.colors import Color
from compas.geometry import Brep
from compas_view2.app import App

A = Box(1).to_brep()

box = Box(1)
box.translate([1, 0.3, 0.5])
B = Brep.from_box(box)

FA, FB = A.overlap(B)

# =============================================================================
# Visualization
# =============================================================================

viewer = App()
viewer.view.camera.position = [3, -3, 1]
viewer.view.camera.look_at([-1, 2, 0])

viewer.add(A, opacity=0.5, linewidth=3)
viewer.add(B, opacity=0.5, linewidth=3)

for face in FA[:1]:
    brep = Brep.from_brepfaces([face])
    viewer.add(
        brep,
        facecolor=Color.red().lightened(50),
        linewidth=3,
        linecolor=Color.red(),
    )

for face in FB[:1]:
    brep = Brep.from_brepfaces([face])
    viewer.add(
        brep,
        facecolor=Color.blue().lightened(50),
        linewidth=3,
        linecolor=Color.blue(),
    )

viewer.show()
