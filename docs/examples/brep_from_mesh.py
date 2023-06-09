import compas
from compas.geometry import Vector, Translation, Scale
from compas.geometry import Polyline
from compas.datastructures import Mesh
from compas_occ.brep import BRep
from compas_view2.app import App


mesh = Mesh.from_obj(compas.get("tubemesh.obj"))

centroid = mesh.centroid()
zmin = min(mesh.vertices_attribute("z"))
vector = Vector(*centroid)
vector.z = zmin
vector *= -1

T = Translation.from_vector(vector)
S = Scale.from_factors([0.3, 0.3, 0.3])

mesh.transform(S * T)

brep = BRep.from_mesh(mesh)
brep.check()

lines = []
curves = []

for edge in brep.edges:
    if edge.is_line:
        lines.append(edge.to_line())
    elif edge.is_bspline:
        curves.append(Polyline(edge.curve.locus()))

viewer = App(viewmode="ghosted")
viewer.add(brep, show_lines=False)

for curve in curves:
    viewer.add(curve, linewidth=2)

viewer.run()
