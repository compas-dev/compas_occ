import compas
from compas.geometry import Plane
from compas_occ.geometry import OCCSurface
from compas_occ.brep import BRepFace
from compas_occ.brep import BRep

from OCC.Core.BRep import BRep_Tool_Surface
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAdaptor import GeomAdaptor_Surface

plane = Plane.worldXY()

surface = OCCSurface.from_plane(plane)

face = BRepFace.from_surface(surface)

brep = BRep.from_faces([face])

for face in brep.faces:
    print(face.is_plane)

    result = BRep_Tool_Surface(face.occ_face)
    print(result)

    result = BRepAdaptor_Surface(face.occ_face).Plane()
    print(result)

    result = GeomAdaptor_Surface(BRep_Tool_Surface(face.occ_face)).Plane()
    print(result)
