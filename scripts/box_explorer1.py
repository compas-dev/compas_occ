from afem.topology.create import BoxBySize
from compas.datastructures import Mesh
from compas.geometry import Point

box = BoxBySize(1, 1, 1)
polygons = []

for f in box.solid.faces:
    points = []
    for v in f.vertices:
        pt = Point(*v.point.XYZ().Coord())
        points.append(pt)

    polygons.append(points)

mesh = Mesh.from_polygons(polygons)
