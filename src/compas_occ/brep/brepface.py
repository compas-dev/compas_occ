from typing import Optional

from OCC.Core import BRepAdaptor
from OCC.Core import BRepAlgo
from OCC.Core import BRepBuilderAPI
from OCC.Core import BRepGProp
from OCC.Core import BRepTools
from OCC.Core import GeomAbs
from OCC.Core import GeomConvert
from OCC.Core import GProp
from OCC.Core import ShapeFix
from OCC.Core import TopAbs
from OCC.Core import TopExp
from OCC.Core import TopoDS
from OCC.Core import gp

import compas.geometry
import compas_occ.conversions
from compas.geometry import BrepFace
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import Frame
from compas.geometry import NurbsSurface
from compas.geometry import Plane
from compas.geometry import Polygon
from compas.geometry import Sphere
from compas.geometry import SurfaceType
from compas.geometry import Torus
from compas_occ.brep import OCCBrepEdge
from compas_occ.brep import OCCBrepLoop
from compas_occ.brep import OCCBrepVertex
from compas_occ.brep.brepedge import CurveType
from compas_occ.conversions import cone_to_occ
from compas_occ.conversions import cylinder_to_compas
from compas_occ.conversions import cylinder_to_occ
from compas_occ.conversions import plane_to_compas
from compas_occ.conversions import plane_to_occ
from compas_occ.conversions import point_to_compas
from compas_occ.conversions import sphere_to_compas
from compas_occ.conversions import sphere_to_occ
from compas_occ.conversions import torus_to_occ
from compas_occ.geometry import OCCNurbsSurface
from compas_occ.geometry import OCCSurface


class OCCBrepFace(BrepFace):
    """
    Class representing a face in the BRep of a geometric shape.

    Parameters
    ----------
    occ_face : ``TopoDS.TopoDS_Face``
        An OCC BRep face.

    Attributes
    ----------
    vertices : list[:class:`~compas_occ.brep.BrepVertex`], read-only
        List of BRep vertices.
    edges : list[:class:`~compas_occ.brep.BrepEdge`], read-only
        List of BRep edges.
    loops : list[:class:`~compas_occ.brep.BrepLoop`], read-only
        List of BRep loops.
    surface : ``GeomAdaptor_Surface``
        Surface geometry from the adaptor.

    """

    _occ_face: TopoDS.TopoDS_Face

    @property
    def __data__(self) -> dict:
        loops = []
        for loop in self.loops:
            edges = []
            for edge in loop.edges:
                edgedata = {
                    "type": edge.type,
                    "curve": edge.curve,
                    "domain": edge.domain,
                    "start": edge.first_vertex.point,
                    "end": edge.last_vertex.point,
                    "orientation": edge.orientation,
                    "dimension": 3,
                }
                if edge.type == CurveType.CURVE2D:
                    adaptor2 = BRepAdaptor.BRepAdaptor_Curve2d(edge.occ_edge, self.occ_face)
                    type2 = adaptor2.GetType()

                    if type2 == GeomAbs.GeomAbs_CurveType.GeomAbs_Line:
                        ctype = CurveType.LINE
                        curve = compas_occ.conversions.line2d_to_compas(adaptor2.Line())

                    elif type2 == GeomAbs.GeomAbs_CurveType.GeomAbs_Circle:
                        ctype = CurveType.CIRCLE
                        curve = compas_occ.conversions.circle2d_to_compas(adaptor2.Circle())

                    elif type2 == GeomAbs.GeomAbs_CurveType.GeomAbs_Ellipse:
                        ctype = CurveType.ELLIPSE
                        curve = compas_occ.conversions.ellipse2d_to_compas(adaptor2.Ellipse())

                    elif type2 == GeomAbs.GeomAbs_CurveType.GeomAbs_Hyperbola:
                        ctype = CurveType.HYPERBOLA
                        curve = compas_occ.conversions.hyperbola2d_to_compas(adaptor2.Hyperbola())

                    elif type2 == GeomAbs.GeomAbs_CurveType.GeomAbs_Parabola:
                        ctype = CurveType.PARABOLA
                        curve = compas_occ.conversions.parabola2d_to_compas(adaptor2.Parabola())

                    else:
                        raise NotImplementedError

                    edgedata["type"] = ctype
                    edgedata["curve"] = curve
                    edgedata["domain"] = [adaptor2.FirstParameter(), adaptor2.LastParameter()]
                    edgedata["dimension"] = 2

                edges.append(edgedata)
            loops.append(edges)

        data = {
            "type": self.type,
            "surface": self.surface,
            "domain_u": self.domain_u,
            "domain_v": self.domain_v,
            "frame": Frame.worldXY(),
            "loops": loops,
            "orientation": self.orientation,
        }
        return data

    @classmethod
    def __from_data__(cls, data: dict) -> "OCCBrepFace":
        """Construct an object of this type from the provided data.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        :class:`OCCBrepFace`
            An instance of this object type if the data contained in the dict has the correct schema.

        """
        raise NotImplementedError

    def __init__(self, occ_face: TopoDS.TopoDS_Face):
        super().__init__()
        self.precision = 1e-6
        self._surface = None
        self._nurbssurface = None
        self._occ_adaptor = None
        self._occ_face = occ_face

    def __eq__(self, other: "OCCBrepFace") -> bool:
        return self.is_equal(other)

    def is_same(self, other: "OCCBrepFace") -> bool:
        """Check if this face is the same as another face.

        Two faces are the same if they have the same location.

        Parameters
        ----------
        other : :class:`OCCBrepFace`
            The other face.

        Returns
        -------
        bool
            ``True`` if the faces are the same, ``False`` otherwise.

        """
        if not isinstance(other, OCCBrepFace):
            return False
        return self.occ_face.IsSame(other.occ_face)

    def is_equal(self, other: "OCCBrepFace") -> bool:
        """Check if this face is equal to another face.

        Two faces are equal if they have the same location and orientation.

        Parameters
        ----------
        other : :class:`OCCBrepFace`
            The other face.

        Returns
        -------
        bool
            ``True`` if the faces are equal, ``False`` otherwise.

        """
        if not isinstance(other, OCCBrepFace):
            return False
        return self.occ_face.IsEqual(other.occ_face)

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_shape(self) -> TopoDS.TopoDS_Face:
        return self.occ_face

    @property
    def occ_face(self) -> TopoDS.TopoDS_Face:
        return self._occ_face

    @occ_face.setter
    def occ_face(self, face: TopoDS.TopoDS_Face) -> None:
        self._occ_adaptor = None
        self._surface = None
        self._nurbssurface = None
        self._occ_face = face

    @property
    def occ_adaptor(self) -> BRepAdaptor.BRepAdaptor_Surface:
        if not self._occ_adaptor:
            self._occ_adaptor = BRepAdaptor.BRepAdaptor_Surface(self.occ_face)
        return self._occ_adaptor

    @property
    def orientation(self) -> TopAbs.TopAbs_Orientation:
        return self.occ_face.Orientation()

    # remove this if possible
    @property
    def nurbssurface(self) -> OCCNurbsSurface:
        if not self._nurbssurface:
            occ_surface = self.occ_adaptor.BSpline()
            self._nurbssurface = OCCNurbsSurface(occ_surface)
        return self._nurbssurface

    @property
    def surface(self):
        if self.is_plane:
            return self.to_plane()
        if self.is_cylinder:
            return self.to_cylinder()
        if self.is_cone:
            return self.to_cone()
        if self.is_sphere:
            return self.to_sphere()
        if self.is_torus:
            return self.to_torus()
        if self.is_bspline:
            return self.to_nurbs()
        raise NotImplementedError

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def type(self) -> int:
        return self.occ_adaptor.GetType()

    @property
    def is_plane(self) -> bool:
        return self.type == SurfaceType.PLANE

    @property
    def is_cylinder(self) -> bool:
        return self.type == SurfaceType.CYLINDER

    @property
    def is_sphere(self) -> bool:
        return self.type == SurfaceType.SPHERE

    @property
    def is_torus(self) -> bool:
        return self.type == SurfaceType.TORUS

    @property
    def is_cone(self) -> bool:
        return self.type == SurfaceType.CONE

    @property
    def is_bezier(self) -> bool:
        return self.type == SurfaceType.BEZIER_SURFACE

    @property
    def is_bspline(self) -> bool:
        return self.type == SurfaceType.BSPLINE_SURFACE

    # other types of surfaces:
    # -----------------------
    # revolved
    # extruded
    # offset
    # other

    @property
    def vertices(self) -> list[OCCBrepVertex]:
        vertices = []
        explorer = TopExp.TopExp_Explorer(self.occ_face, TopAbs.TopAbs_VERTEX)  # type: ignore
        while explorer.More():
            vertex = explorer.Current()
            vertices.append(OCCBrepVertex(vertex))  # type: ignore
            explorer.Next()
        return vertices

    @property
    def edges(self) -> list[OCCBrepEdge]:
        edges = []
        explorer = TopExp.TopExp_Explorer(self.occ_face, TopAbs.TopAbs_EDGE)  # type: ignore
        while explorer.More():
            edge = explorer.Current()
            edges.append(OCCBrepEdge(edge))  # type: ignore
            explorer.Next()
        return edges

    @property
    def loops(self) -> list[OCCBrepLoop]:
        loops = []
        explorer = TopExp.TopExp_Explorer(self.occ_face, TopAbs.TopAbs_WIRE)  # type: ignore
        while explorer.More():
            wire = explorer.Current()
            loops.append(OCCBrepLoop(wire))  # type: ignore
            explorer.Next()
        return loops

    @property
    def outerloop(self) -> OCCBrepLoop:
        wire = BRepTools.breptools.OuterWire(self.occ_face)
        return OCCBrepLoop(wire)

    @property
    def innerloops(self) -> list[OCCBrepLoop]:
        outerloop = self.outerloop
        inner = []
        for loop in self.loops:
            if not loop.is_same(outerloop):
                inner.append(loop)
        return inner

    @property
    def area(self) -> float:
        props = GProp.GProp_GProps()
        BRepGProp.brepgprop.SurfaceProperties(self.occ_shape, props)
        return props.Mass()

    @property
    def centroid(self) -> compas.geometry.Point:
        props = GProp.GProp_GProps()
        BRepGProp.brepgprop.VolumeProperties(self.occ_shape, props)
        pnt = props.CentreOfMass()
        return point_to_compas(pnt)

    @property
    def domain_u(self) -> tuple[float, float]:
        return self.occ_adaptor.FirstUParameter(), self.occ_adaptor.LastUParameter()

    @property
    def domain_v(self) -> tuple[float, float]:
        return self.occ_adaptor.FirstVParameter(), self.occ_adaptor.LastVParameter()

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_polygon(cls, points: Polygon) -> "OCCBrepFace":
        """
        Construct a BRep face from a polygon.

        Parameters
        ----------
        polygon : :class:`compas.geometry.Polygon`

        Returns
        -------
        :class:`OCCBrepFace`

        """
        polygon = BRepBuilderAPI.BRepBuilderAPI_MakePolygon()
        for point in points:
            polygon.Add(gp.gp_Pnt(*point))
        polygon.Close()
        wire = polygon.Wire()
        return cls(BRepBuilderAPI.BRepBuilderAPI_MakeFace(wire).Face())

    @classmethod
    def from_plane(
        cls,
        plane: Plane,
        domain_u: Optional[tuple[float, float]] = None,
        domain_v: Optional[tuple[float, float]] = None,
        loop: Optional[OCCBrepLoop] = None,
        inside: bool = True,
    ) -> "OCCBrepFace":
        """
        Construct a face from a plane.

        Parameters
        ----------
        plane : :class:`compas.geometry.Plane`
            The plane.
        domain_u : tuple[float, float], optional
            U parameter minimum and maximum.
        domain_v : tuple[float, float], optional
            V parameter minimum and maximum.
        loop : :class:`compas_occ.brep.OCCBrepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`OCCBrepFace`

        """
        occ_plane: gp.gp_Pln = plane_to_occ(plane)
        if domain_u and domain_v:
            min_u, max_u = domain_u
            min_v, max_v = domain_v
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(occ_plane, min_u, max_u, min_v, max_v)
        elif loop:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(occ_plane, loop.occ_wire, inside)
        else:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(occ_plane)
        return cls(builder.Face())

    @classmethod
    def from_cylinder(
        cls,
        cylinder: Cylinder,
        loop: Optional[OCCBrepLoop] = None,
        inside: bool = True,
    ) -> "OCCBrepFace":
        """
        Construct a face from a cylinder.

        Parameters
        ----------
        cylinder : :class:`compas.geometry.Cylinder`
            The cylinder.
        loop : :class:`compas_occ.brep.OCCBrepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`OCCBrepFace`

        """
        if loop:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(
                cylinder_to_occ(cylinder),
                loop.occ_wire,
                inside,
            )
        else:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(cylinder_to_occ(cylinder))
        return cls(builder.Face())

    @classmethod
    def from_cone(
        cls,
        cone: Cone,
        loop: Optional[OCCBrepLoop] = None,
        inside: bool = True,
    ) -> "OCCBrepFace":
        """
        Construct a face from a cone.

        Parameters
        ----------
        cone : :class:`compas.geometry.Cone`
            The cone.
        loop : :class:`compas_occ.brep.OCCBrepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`OCCBrepFace`

        """
        if loop:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(
                cone_to_occ(cone),
                loop.occ_wire,
                inside,
            )
        else:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(cone_to_occ(cone))
        return cls(builder.Face())

    @classmethod
    def from_sphere(
        cls,
        sphere: Sphere,
        loop: Optional[OCCBrepLoop] = None,
        inside: bool = True,
    ) -> "OCCBrepFace":
        """
        Construct a face from a sphere.

        Parameters
        ----------
        sphere : :class:`compas.geometry.Sphere`
            The sphere.
        loop : :class:`compas_occ.brep.OCCBrepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`OCCBrepFace`

        """
        if loop:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(sphere_to_occ(sphere), loop.occ_wire, inside)
        else:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(sphere_to_occ(sphere))
        return cls(builder.Face())

    @classmethod
    def from_torus(
        cls,
        torus: Torus,
        loop: Optional[OCCBrepLoop] = None,
        inside: bool = True,
    ) -> "OCCBrepFace":
        """
        Construct a face from a torus.

        Parameters
        ----------
        torus : :class:`compas.geometry.Torus`
            The torus.
        loop : :class:`compas_occ.brep.OCCBrepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`OCCBrepFace`

        """
        if loop:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(torus_to_occ(torus), loop.occ_wire, inside)
        else:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(torus_to_occ(torus))
        return cls(builder.Face())

    @classmethod
    def from_surface(
        cls,
        surface: OCCSurface,
        domain_u: Optional[tuple[float, float]] = None,
        domain_v: Optional[tuple[float, float]] = None,
        precision: float = 1e-6,
        loop: Optional[OCCBrepLoop] = None,
        inside: bool = True,
    ) -> "OCCBrepFace":
        """
        Construct a face from a surface.

        Parameters
        ----------
        surface : :class:`compas_occ.geometry.OCCSurface`
            The torus.
        domain_u : tuple[float, float], optional
            U parameter minimum and maximum.
        domain_v : tuple[float, float], optional
            V parameter minimum and maximum.
        precision : float, optional
            Precision for face construction.
        loop : :class:`compas_occ.brep.OCCBrepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`OCCBrepFace`

        """
        if domain_u and domain_v:
            min_u, max_u = domain_u
            min_v, max_v = domain_v
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(surface.occ_surface, min_u, max_u, min_v, max_v, precision)
        elif loop:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(surface.occ_surface, loop.occ_wire, inside)
        else:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(surface.occ_surface, precision)
        face = cls(builder.Face())
        face.precision = precision
        return face

    # ==============================================================================
    # Conversions
    # ==============================================================================

    def to_polygon(self) -> Polygon:
        """
        Convert the face to a polygon without underlying geometry.

        Returns
        -------
        :class:`Polygon`

        """
        return self.outerloop.to_polygon()

    def to_polygons(self) -> list[Polygon]:
        """
        Convert the face to polygons without underlying geometry.

        Returns
        -------
        list[:class:`Polygon`]

        """
        return [loop.to_polygon() for loop in self.loops]

    def to_plane(self) -> Plane:
        """
        Convert the face surface geometry to a plane.

        Returns
        -------
        :class:`compas.geometry.Plane`

        """
        if not self.is_plane:
            raise Exception("Face is not a plane.")

        plane = self.occ_adaptor.Plane()
        return plane_to_compas(plane)

    def to_cylinder(self) -> Cylinder:
        """
        Convert the face surface geometry to a cylinder.

        Returns
        -------
        :class:`compas.geometry.Cylinder`

        """
        if not self.is_cylinder:
            raise Exception("Face is not a cylinder.")

        cylinder = self.occ_adaptor.Cylinder()
        return cylinder_to_compas(cylinder)

    def to_cone(self) -> Cone:
        """
        Convert the face surface geometry to a cone.

        Returns
        -------
        :class:`compas.geometry.Cone`

        """
        raise NotImplementedError

    def to_sphere(self) -> Sphere:
        """
        Convert the face surface geometry to a sphere.

        Returns
        -------
        :class:`compas.geometry.Sphere`

        """
        if not self.is_sphere:
            raise Exception("Face is not a sphere.")

        sphere = self.occ_adaptor.Sphere()
        return sphere_to_compas(sphere)

    def to_torus(self) -> Torus:
        """
        Convert the face surface geometry to a torus.

        Returns
        -------
        :class:`compas.geometry.Torus`

        """
        raise NotImplementedError

    def to_nurbs(self) -> NurbsSurface:
        """
        Convert the face surface geometry to a torus.

        Returns
        -------
        :class:`compas.geometry.NurbsSurface`

        """
        if not self.is_bspline:
            raise Exception("Face is not a nurbs surface.")

        bspline = self.occ_adaptor.BSpline()
        return NurbsSurface.from_native(bspline)

    # ==============================================================================
    # Methods
    # ==============================================================================

    def try_get_nurbssurface(
        self,
        precision=1e-3,
        continuity_u=None,
        continuity_v=None,
        maxdegree_u=5,
        maxdegree_v=5,
        maxsegments_u=1,
        maxsegments_v=1,
    ) -> OCCNurbsSurface:
        """
        Try to convert the underlying geometry to a Nurbs surface.

        """
        try:
            occ_surface = self.occ_adaptor.BSpline()
        except Exception:
            convert = GeomConvert.GeomConvert_ApproxSurface(
                self.occ_adaptor.Surface().Surface(),
                precision,
                GeomAbs.GeomAbs_Shape.GeomAbs_C1,  # type: ignore
                GeomAbs.GeomAbs_Shape.GeomAbs_C1,  # type: ignore
                maxdegree_u,
                maxdegree_v,
                maxsegments_u,
                maxsegments_v,
            )  # type: ignore
            occ_surface = convert.Surface()
        return OCCNurbsSurface(occ_surface)

    def is_valid(self) -> bool:
        """
        Verify that the face is valid.

        Returns
        -------
        bool

        """
        return BRepAlgo.brepalgo.IsValid(self.occ_face)

    def fix(self) -> None:
        """
        Try to fix the face.

        Returns
        -------
        None

        """
        fixer = ShapeFix.ShapeFix_Face(self.occ_face)
        fixer.Perform()
        self.occ_face = fixer.Face()

    def add_loop(self, loop: OCCBrepLoop, reverse: bool = False) -> None:
        """
        Add an inner loop to the face.

        Parameters
        ----------
        loop : :class:`compas_occ.brep.OCCBrepLoop`
            The additional loop.

        Returns
        -------
        None

        """
        builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(self.occ_face)
        if reverse:
            builder.Add(loop.occ_wire.Reversed())  # type: ignore
        else:
            builder.Add(loop.occ_wire)
        if not builder.IsDone():
            raise Exception(builder.Error())
        self.occ_face = builder.Face()

    def add_loops(self, loops: list[OCCBrepLoop], reverse: bool = False) -> None:
        """
        Add an inner loop to the face.

        Parameters
        ----------
        loops : list[:class:`compas_occ.brep.OCCBrepLoop`]
            The additional loops.

        Returns
        -------
        None

        """
        builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(self.occ_face)
        for loop in loops:
            if reverse:
                builder.Add(loop.occ_wire.Reversed())  # type: ignore
            else:
                builder.Add(loop.occ_wire)
        if not builder.IsDone():
            raise Exception(builder.Error())
        self.occ_face = builder.Face()
