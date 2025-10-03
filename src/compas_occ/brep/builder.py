from typing import Optional

from OCC.Core import BRep
from OCC.Core import BRepAlgo
from OCC.Core import BRepBuilderAPI
from OCC.Core import Geom
from OCC.Core import Geom2d
from OCC.Core import ShapeFix
from OCC.Core import TopAbs
from OCC.Core import TopoDS

from compas.geometry import CurveType
from compas.geometry import SurfaceType
from compas_occ import conversions

from .brep import OCCBrep


class OCCBrepBuilder:
    """Class for building OCC Breps from serialisation data.

    Parameters
    ----------
    make_solid : bool, optional
    """

    def __init__(self, make_solid: Optional[bool] = True):
        self.shell = TopoDS.TopoDS_Shell()
        self.builder = BRep.BRep_Builder()
        self.builder.MakeShell(self.shell)
        self.make_solid = make_solid

    def build(self, faces: list[dict]) -> OCCBrep:
        """Build a COMPAS OCC brep from list of faces represented by their serialisation data.

        Parameters
        ----------
        faces : list[dict]
            A list of faces represented by their serialisation data.

        Returns
        -------
        :class:`OCCBrep`

        """
        for facedata in faces:
            face = self.build_face(facedata)
            self.builder.Add(self.shell, face)

        brep = OCCBrep.from_native(self.shell)
        brep.heal()
        if self.make_solid:
            brep.make_solid()
        return brep

    def build_edge(self, edgedata: dict) -> TopoDS.TopoDS_Edge:
        """Build an OCC edge from edge serialisation data with 3D curve geometry.

        Parameters
        ----------
        edgedata : dict
            The serialisation data representing an edge.

        Returns
        -------
        `TopoDS.TopoDS_Edge`

        """
        start = conversions.point_to_occ(edgedata["start"])
        end = conversions.point_to_occ(edgedata["end"])
        u, v = edgedata["domain"]

        if edgedata["type"] == CurveType.LINE:
            curve = conversions.line_to_occ(edgedata["curve"])
            params = [start, end]

        elif edgedata["type"] == CurveType.CIRCLE:
            curve = Geom.Geom_Circle(conversions.circle_to_occ(edgedata["curve"]))
            params = [start, end, u, v]

        elif edgedata["type"] == CurveType.ELLIPSE:
            curve = Geom.Geom_Ellipse(conversions.ellipse_to_occ(edgedata["curve"]))
            params = [start, end, u, v]

        elif edgedata["type"] == CurveType.BSPLINE:
            curve = edgedata["curve"].native_curve
            params = [start, end, u, v]

        else:
            raise NotImplementedError

        return BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve, *params).Edge()

    def build_edge2d(self, edgedata, surface: Geom.Geom_Surface) -> TopoDS.TopoDS_Edge:
        """Build an OCC edge from edge serialisation data with 2D curve geometry embedded on a surface.

        Parameters
        ----------
        edgedata : dict
            The serialisation data representing an edge.

        Returns
        -------
        `TopoDS.TopoDS_Edge`

        """
        start = conversions.point_to_occ(edgedata["start"])
        end = conversions.point_to_occ(edgedata["end"])

        u, v = edgedata["domain"]

        if edgedata["type"] == CurveType.LINE:
            curve = Geom2d.Geom2d_Line(conversions.line_to_occ2d(edgedata["curve"]))
            params = [start, end, u, v]

        elif edgedata["type"] == CurveType.CIRCLE:
            curve = Geom2d.Geom2d_Circle(conversions.circle_to_occ2d(edgedata["curve"]))
            params = [start, end, u, v]

        elif edgedata["type"] == CurveType.ELLIPSE:
            curve = Geom2d.Geom2d_Ellipse(conversions.ellipse_to_occ2d(edgedata["curve"]))
            params = [start, end, u, v]

        elif edgedata["type"] == CurveType.BSPLINE:
            curve = edgedata["curve"].native_curve
            params = [start, end, u, v]

        else:
            raise NotImplementedError

        return BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve, surface, *params).Edge()

    def build_wire(self, edges: list[dict], surface: Geom.Geom_Surface) -> TopoDS.TopoDS_Wire:
        """Build an OCC wire from a list of edges represented by their serialisation data.

        Parameters
        ----------
        edges : list[dict]
            The serialisation data of the edges.
        surface : `Geom.Geom_Surface`
            The surface geometry of the face of the wire.

        Returns
        -------
        `TopoDS.TopoDS_Wire`

        """
        builder = BRepBuilderAPI.BRepBuilderAPI_MakeWire()

        for edgedata in edges:
            if edgedata["dimension"] == 2:
                edge = self.build_edge2d(edgedata, surface)
            else:
                edge = self.build_edge(edgedata)

            if edgedata["orientation"] != edge.Orientation():
                edge.Orientation(TopAbs.TopAbs_Orientation(edgedata["orientation"]))

            builder.Add(edge)

        return builder.Wire()

    def build_face(self, data) -> TopoDS.TopoDS_Face:
        """Build an OCC face from face serialisation data.

        Parameters
        ----------
        data : dict
            The serialisation data of the face.

        Returns
        -------
        `TopoDS.TopoDS_Face`

        """
        if data["type"] == SurfaceType.PLANE:
            plane = conversions.plane_to_occ(data["surface"])
            surface = Geom.Geom_Plane(plane)

        elif data["type"] == SurfaceType.CYLINDER:
            cylinder = conversions.cylinder_to_occ(data["surface"])
            surface = Geom.Geom_CylindricalSurface(cylinder)

        elif data["type"] == SurfaceType.SPHERE:
            sphere = conversions.sphere_to_occ(data["surface"])
            surface = Geom.Geom_SphericalSurface(sphere)

        elif data["type"] == SurfaceType.BSPLINE_SURFACE:
            surface = data["surface"].native_surface

        else:
            raise NotImplementedError

        loops = data["loops"]
        boundary = self.build_wire(loops[0], surface)
        builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(surface, boundary)

        if len(loops) > 1:
            for edges in loops[1:]:
                hole = self.build_wire(edges, surface)
                builder.Add(hole)

        face = builder.Face()

        if data["orientation"] != face.Orientation():
            face.Orientation(TopAbs.TopAbs_Orientation(data["orientation"]))

        if not BRepAlgo.brepalgo.IsValid(face):
            fixer = ShapeFix.ShapeFix_Face(face)
            fixer.Perform()
            face = fixer.Face()

        return face
