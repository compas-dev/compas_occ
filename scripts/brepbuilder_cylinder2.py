from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from compas.geometry import Brep
from compas.geometry import Cylinder
from compas.geometry import SurfaceType
from compas_occ.brep import OCCBrepFace
from compas_occ import conversions

from compas_view2.app import App

cylinder = Brep.from_cylinder(Cylinder(1.0, 2.0))

facedata = []
for face in cylinder.faces:  # type: ignore
    loops = [face.outerloop] + face.innerloops
    facedata.append(
        {
            "type": face.type,
            "surface": face.surface,
            "domain_u": face.domain_u,
            "domain_v": face.domain_v,
            "loops": loops,
        }
    )

faces = []
for data in facedata:
    if data["type"] == SurfaceType.PLANE:
        surface = conversions.plane_to_occ(data["surface"])
        builder = BRepBuilderAPI_MakeFace(surface, data["loops"][0].occ_wire)
        # if len(data["loops"]) > 1:
        #     for loop in data["loops"][1:]:
        #         builder.Add(loop.occ_wire)
        faces.append(builder.Face())

    elif data["type"] == SurfaceType.CYLINDER:
        surface = conversions.cylinder_to_occ(data["surface"])
        face = BRepBuilderAPI_MakeFace(
            surface,
            *data["domain_u"],
            *data["domain_v"],
        ).Face()
        builder = BRepBuilderAPI_MakeFace(face, data["loops"][0].occ_wire)
        # if len(data["loops"]) > 1:
        #     for loop in data["loops"][1:]:
        #         builder.Add(loop.occ_wire)
        faces.append(builder.Face())

brep = Brep.from_brepfaces([OCCBrepFace(face) for face in faces])
# brep.make_solid()
brep.fix()
brep.sew()

viewer = App()
viewer.add(brep)  # type: ignore
viewer.show()
