# type: ignore
from math import radians
from compas.geometry import Box, Plane, Rotation
from compas.geometry import is_point_infrontof_plane
from compas.colors import Color
from compas_occ.brep import OCCBrep as Brep
from compas_view2.app import App

box = Box(1).to_brep()

R = Rotation.from_axis_and_angle([0, 1, 0], radians(30))
plane = Plane.worldXY()
plane.transform(R)

result = box.split(Brep.from_planes([plane]))

# =============================================================================
# Visualization
# =============================================================================

viewer = App()
viewer.view.camera.position = [2, -4, 1]
viewer.view.camera.look_at([0, 0, 0])

viewer.add(
    plane, linewidth=2, opacity=0.3
)  # there is a debug print statement in the viewer that needs to be removed

for brep in result:
    if is_point_infrontof_plane(brep.centroid, plane):
        viewer.add(
            brep,
            facecolor=Color.red().lightened(50),
            linecolor=Color.red(),
            linewidth=2,
        )
    else:
        viewer.add(
            brep,
            facecolor=Color.blue().lightened(50),
            linecolor=Color.blue(),
            linewidth=2,
        )

viewer.show()
