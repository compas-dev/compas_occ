from OCCUtils import Topo
from OCCUtils.Common import vertex2pnt
from OCCUtils.Construct import make_box
from compas.datastructures import Mesh

box = make_box(1, 1, 1)

polygons = []

topo = Topo(box)

for f in topo.faces():
    points = []
    for v in Topo(f).vertices():
        pt = vertex2pnt(v).to_compas()
        points.append(pt)

mesh = Mesh.from_polygons(polygons)

