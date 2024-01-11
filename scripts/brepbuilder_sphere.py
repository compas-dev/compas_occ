from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.TopAbs import TopAbs_Orientation
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve2d
from OCC.Core.GeomAbs import GeomAbs_CurveType

from compas.geometry import Brep
from compas.geometry import Sphere
from compas.geometry import SurfaceType
from compas.geometry import CurveType
from compas_occ.brep import OCCBrepFace
from compas_occ import conversions

from compas_view2.app import App


def BuildWireFromEdges(edges, surface):
    builder = BRepBuilderAPI_MakeWire()

    for edgedata in edges:
        if edgedata["dimension"] == 3:
            if edgedata["type"] == CurveType.LINE:
                curve = conversions.line_to_occ(edgedata["curve"])
            elif edgedata["type"] == CurveType.CIRCLE:
                curve = conversions.circle_to_occ(edgedata["curve"])
            else:
                raise NotImplementedError

            edge = BRepBuilderAPI_MakeEdge(curve, *edgedata["domain"]).Edge()

        elif edgedata["dimension"] == 2:
            if edgedata["type"] == CurveType.LINE:
                curve = conversions.line2d_to_occ(edgedata["curve"])
            elif edgedata["type"] == CurveType.CIRCLE:
                curve = conversions.circle2d_to_occ(edgedata["curve"])
            else:
                raise NotImplementedError

            edge = BRepBuilderAPI_MakeEdge(curve, surface, *edgedata["domain"]).Edge()

        else:
            raise NotImplementedError

        if edgedata["orientation"] != edge.Orientation():
            edge.Orientation(TopAbs_Orientation(edgedata["orientation"]))

        builder.Add(edge)

    wire = builder.Wire()
    return wire


sphere = Brep.from_sphere(Sphere(1.0))

# convert to data

facedata = []
for face in sphere.faces:  # type: ignore
    boundary = []
    for edge in face.outerloop.edges:
        if edge.type == CurveType.CURVE2D:
            adaptor2 = BRepAdaptor_Curve2d(edge.occ_edge, face.occ_face)
            type2 = adaptor2.GetType()
            domain2 = adaptor2.FirstParameter(), adaptor2.LastParameter()
            if type2 == GeomAbs_CurveType.GeomAbs_Line:
                curve = conversions.line2d_to_compas(adaptor2.Line())
        else:
            edge_type = edge.type
            edge_curve = edge.curve
            edge_domain = edge.domain
            edge_orientation = edge.orientation
            edge_dimension = 3
        boundary.append(
            {
                "type": edge_type,
                "curve": edge_curve,
                "domain": edge_domain,
                "orientation": edge_orientation,
                "dimension": edge_dimension,
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
                    "orientation": edge.orientation,
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

# reconstruct from data

faces = []
for data in facedata:
    if data["type"] == SurfaceType.PLANE:
        surface = conversions.plane_to_occ(data["surface"])
        boundary = BuildWireFromEdges(data["boundary"], surface)
        builder = BRepBuilderAPI_MakeFace(surface, boundary)
        for edges in data["holes"]:
            hole = BuildWireFromEdges(edges, surface)
            builder.Add(hole)
        face = builder.Face()

    elif data["type"] == SurfaceType.CYLINDER:
        surface = conversions.cylinder_to_occ(data["surface"])
        face = BRepBuilderAPI_MakeFace(
            surface, *data["domain_u"], *data["domain_v"]
        ).Face()
        boundary = BuildWireFromEdges(data["boundary"], surface)
        builder = BRepBuilderAPI_MakeFace(face, boundary)
        for edges in data["holes"]:
            hole = BuildWireFromEdges(edges, surface)
            builder.Add(hole)
        face = builder.Face()

    elif data["type"] == SurfaceType.SPHERE:
        surface = conversions.sphere_to_occ(data["surface"])
        face = BRepBuilderAPI_MakeFace(
            surface, *data["domain_u"], *data["domain_v"]
        ).Face()
        boundary = BuildWireFromEdges(data["boundary"], surface)
        builder = BRepBuilderAPI_MakeFace(face, boundary)
        for edges in data["holes"]:
            hole = BuildWireFromEdges(edges, surface)
            builder.Add(hole)
        face = builder.Face()

    else:
        raise NotImplementedError

    if data["orientation"] != face.Orientation():
        face.Orientation(TopAbs_Orientation(data["orientation"]))
    faces.append(face)


brep = Brep.from_brepfaces([OCCBrepFace(face) for face in faces])
brep.make_solid()
brep.fix()
brep.sew()

viewer = App()
viewer.add(brep)  # type: ignore
viewer.show()
