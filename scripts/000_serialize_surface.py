import compas
from compas.geometry import Plane
from compas_occ.geometry import OCCSurface

plane = Plane.worldXY()

surface = OCCSurface.from_plane(plane)

print(surface)
