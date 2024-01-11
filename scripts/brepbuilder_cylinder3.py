from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.TopAbs import TopAbs_Orientation

from compas.geometry import Brep
from compas.geometry import Cylinder
from compas.geometry import SurfaceType
from compas.geometry import CurveType
from compas_occ.brep import OCCBrepFace
from compas_occ import conversions

from compas_view2.app import App


def BuildWireFromEdges(edges):
    builder = BRepBuilderAPI_MakeWire()

    for edgedata in edges:
        if edgedata["type"] == CurveType.LINE:
            curve = conversions.line_to_occ(edgedata["curve"])
        elif edgedata["type"] == CurveType.CIRCLE:
            curve = conversions.circle_to_occ(edgedata["curve"])
        else:
            raise NotImplementedError

        edge = BRepBuilderAPI_MakeEdge(curve, *edgedata["domain"]).Edge()

        if edgedata["orientation"] != edge.Orientation():
            edge.Orientation(TopAbs_Orientation(edgedata["orientation"]))

        builder.Add(edge)

    wire = builder.Wire()
    return wire


cylinder = Brep.from_cylinder(Cylinder(1.0, 2.0))

facedata = []
for face in cylinder.faces:  # type: ignore
    boundary = []
    for edge in face.outerloop.edges:
        boundary.append(
            {
                "type": edge.type,
                "curve": edge.curve,
                "domain": edge.domain,
                "orientation": edge.occ_orientation,
            }
        )

    holes = []
    for loop in face.innerloops:
        edges = []
        for edge in loop.edges:
            edges.append(
                {
                    "type": edge.type,
                    "curve": edge.curve,
                    "domain": edge.domain,
                    "orientation": edge.occ_orientation,
                }
            )
        holes.append(edges)

    facedata.append(
        {
            "type": face.type,
            "surface": face.surface,
            "domain_u": face.domain_u,
            "domain_v": face.domain_v,
            "boundary": boundary,
            "holes": holes,
            "orientation": face.orientation,
        }
    )

faces = []
for data in facedata:
    if data["type"] == SurfaceType.PLANE:
        surface = conversions.plane_to_occ(data["surface"])
        boundary = BuildWireFromEdges(data["boundary"])
        builder = BRepBuilderAPI_MakeFace(surface, boundary)
        for edges in data["holes"]:
            hole = BuildWireFromEdges(edges)
            builder.Add(hole)
        face = builder.Face()

    elif data["type"] == SurfaceType.CYLINDER:
        surface = conversions.cylinder_to_occ(data["surface"])
        face = BRepBuilderAPI_MakeFace(
            surface, *data["domain_u"], *data["domain_v"]
        ).Face()
        boundary = BuildWireFromEdges(data["boundary"])
        builder = BRepBuilderAPI_MakeFace(face, boundary)
        for edges in data["holes"]:
            hole = BuildWireFromEdges(edges)
            builder.Add(hole)
        face = builder.Face()

    else:
        raise NotImplementedError

    if data["orientation"] != face.Orientation():
        face.Orientation(TopAbs_Orientation(data["orientation"]))
    faces.append(face)

brepfaces = [OCCBrepFace(face) for face in faces]

brep = Brep.from_brepfaces(brepfaces)
brep.make_solid()
brep.fix()
brep.sew()

viewer = App()
viewer.add(brep)  # type: ignore
viewer.show()
