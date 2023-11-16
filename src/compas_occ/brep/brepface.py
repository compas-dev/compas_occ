from typing import List
from typing import Tuple
from typing import Optional
from enum import Enum

from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_VERTEX
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.TopAbs import TopAbs_WIRE
from OCC.Core.TopAbs import TopAbs_Orientation
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepAlgo import brepalgo_IsValid
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.ShapeFix import ShapeFix_Face
from OCC.Core.GProp import GProp_GProps
from OCC.Core.GeomConvert import GeomConvert_ApproxSurface
from OCC.Core.GeomAbs import GeomAbs_Shape
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Pln

import compas.geometry

from compas.geometry import Plane
from compas.geometry import Cylinder
from compas.geometry import Cone
from compas.geometry import Sphere
from compas.geometry import Torus
from compas.geometry import Polygon
from compas.brep import BrepFace

from compas_occ.brep import OCCBrepVertex
from compas_occ.brep import OCCBrepEdge
from compas_occ.brep import OCCBrepLoop

from compas_occ.conversions import compas_point_from_occ_point
from compas_occ.conversions import compas_plane_to_occ_plane
from compas_occ.conversions import compas_cylinder_to_occ_cylinder
from compas_occ.conversions import compas_cone_to_occ_cone
from compas_occ.conversions import compas_sphere_to_occ_sphere
from compas_occ.conversions import compas_torus_to_occ_torus

from compas_occ.geometry import OCCSurface
from compas_occ.geometry import OCCNurbsSurface


class OCCBrepFace(BrepFace):
    """
    Class representing a face in the BRep of a geometric shape.

    Parameters
    ----------
    occ_face : ``TopoDS_Face``
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

    _occ_face: TopoDS_Face

    class SurfaceType(Enum):
        Plane = 0
        Cylinder = 1
        Cone = 2
        Sphere = 3
        Torus = 4
        BezierSurface = 5
        BSplineSurface = 6
        SurfaceOfRevolution = 7
        SurfaceOfExtrusion = 8
        OffsetSurface = 9
        OtherSurface = 10

    def __init__(self, occ_face: TopoDS_Face):
        super().__init__()
        self.precision = 1e-6
        self._surface = None
        self._nurbssurface = None
        self._occ_adaptor = None
        self.occ_face = occ_face

    def __eq__(self, other: "OCCBrepFace"):
        return self.is_equal(other)

    def is_same(self, other: "OCCBrepFace"):
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

    def is_equal(self, other: "OCCBrepFace"):
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
    # Data
    # ==============================================================================

    @property
    def data(self):
        raise NotImplementedError

    @classmethod
    def from_data(cls, data):
        raise NotImplementedError

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_shape(self) -> TopoDS_Face:
        return self.occ_face

    @property
    def occ_face(self) -> TopoDS_Face:
        return self._occ_face

    @occ_face.setter
    def occ_face(self, face: TopoDS_Face) -> None:
        self._occ_adaptor = None
        self._surface = None
        self._nurbssurface = None
        self._occ_face = face

    @property
    def occ_adaptor(self) -> BRepAdaptor_Surface:
        if not self._occ_adaptor:
            self._occ_adaptor = BRepAdaptor_Surface(self.occ_face)
        return self._occ_adaptor

    @property
    def orientation(self) -> TopAbs_Orientation:
        return self.occ_face.Orientation()

    @property
    def surface(self) -> OCCSurface:
        if not self._surface:
            occ_surface = self.occ_adaptor.Surface().Surface()
            self._surface = OCCSurface(occ_surface)
        return self._surface

    @property
    def nurbssurface(self) -> OCCNurbsSurface:
        if not self._nurbssurface:
            occ_surface = self.occ_adaptor.BSpline()
            self._nurbssurface = OCCNurbsSurface(occ_surface)
        return self._nurbssurface

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def type(self) -> int:
        return OCCBrepFace.SurfaceType(self.occ_adaptor.GetType())  # type: ignore

    @property
    def is_plane(self) -> bool:
        return self.type == OCCBrepFace.SurfaceType.Plane

    @property
    def is_cylinder(self) -> bool:
        return self.type == OCCBrepFace.SurfaceType.Cylinder

    @property
    def is_sphere(self) -> bool:
        return self.type == OCCBrepFace.SurfaceType.Sphere

    @property
    def is_torus(self) -> bool:
        return self.type == OCCBrepFace.SurfaceType.Torus

    @property
    def is_cone(self) -> bool:
        return self.type == OCCBrepFace.SurfaceType.Cone

    @property
    def is_bspline(self) -> bool:
        return self.type == OCCBrepFace.SurfaceType.BSplineSurface

    @property
    def vertices(self) -> List[OCCBrepVertex]:
        vertices = []
        explorer = TopExp_Explorer(self.occ_face, TopAbs_VERTEX)
        while explorer.More():
            vertex = explorer.Current()
            vertices.append(OCCBrepVertex(vertex))  # type: ignore
            explorer.Next()
        return vertices

    @property
    def edges(self) -> List[OCCBrepEdge]:
        edges = []
        explorer = TopExp_Explorer(self.occ_face, TopAbs_EDGE)
        while explorer.More():
            edge = explorer.Current()
            edges.append(OCCBrepEdge(edge))  # type: ignore
            explorer.Next()
        return edges

    @property
    def loops(self) -> List[OCCBrepLoop]:
        loops = []
        explorer = TopExp_Explorer(self.occ_face, TopAbs_WIRE)
        while explorer.More():
            wire = explorer.Current()
            loops.append(OCCBrepLoop(wire))  # type: ignore
            explorer.Next()
        return loops

    @property
    def area(self) -> float:
        props = GProp_GProps()
        brepgprop.SurfaceProperties(self.occ_shape, props)
        return props.Mass()

    @property
    def centroid(self) -> compas.geometry.Point:
        props = GProp_GProps()
        brepgprop.VolumeProperties(self.occ_shape, props)
        pnt = props.CentreOfMass()
        return compas_point_from_occ_point(pnt)

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
        polygon = BRepBuilderAPI_MakePolygon()
        for point in points:
            polygon.Add(gp_Pnt(*point))
        polygon.Close()
        wire = polygon.Wire()
        return cls(BRepBuilderAPI_MakeFace(wire).Face())

    @classmethod
    def from_plane(
        cls,
        plane: Plane,
        domain_u: Optional[Tuple[float, float]] = None,
        domain_v: Optional[Tuple[float, float]] = None,
        loop: Optional[OCCBrepLoop] = None,
        inside: bool = True,
    ) -> "OCCBrepFace":
        """
        Construct a face from a plane.

        Parameters
        ----------
        plane : :class:`compas.geometry.Plane`
            The plane.
        domain_u : Tuple[float, float], optional
            U parameter minimum and maximum.
        domain_v : Tuple[float, float], optional
            V parameter minimum and maximum.
        loop : :class:`compas_occ.brep.OCCBrepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`OCCBrepFace`

        """
        occ_plane: gp_Pln = compas_plane_to_occ_plane(plane)
        if domain_u and domain_v:
            min_u, max_u = domain_u
            min_v, max_v = domain_v
            builder = BRepBuilderAPI_MakeFace(occ_plane, min_u, max_u, min_v, max_v)
        elif loop:
            builder = BRepBuilderAPI_MakeFace(occ_plane, loop.occ_wire, inside)
        else:
            builder = BRepBuilderAPI_MakeFace(occ_plane)
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
            builder = BRepBuilderAPI_MakeFace(
                compas_cylinder_to_occ_cylinder(cylinder),
                loop.occ_wire,
                inside,
            )
        else:
            builder = BRepBuilderAPI_MakeFace(compas_cylinder_to_occ_cylinder(cylinder))
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
            builder = BRepBuilderAPI_MakeFace(
                compas_cone_to_occ_cone(cone),
                loop.occ_wire,
                inside,
            )
        else:
            builder = BRepBuilderAPI_MakeFace(compas_cone_to_occ_cone(cone))
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
            builder = BRepBuilderAPI_MakeFace(
                compas_sphere_to_occ_sphere(sphere), loop.occ_wire, inside
            )
        else:
            builder = BRepBuilderAPI_MakeFace(compas_sphere_to_occ_sphere(sphere))
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
            builder = BRepBuilderAPI_MakeFace(
                compas_torus_to_occ_torus(torus), loop.occ_wire, inside
            )
        else:
            builder = BRepBuilderAPI_MakeFace(compas_torus_to_occ_torus(torus))
        return cls(builder.Face())

    @classmethod
    def from_surface(
        cls,
        surface: OCCSurface,
        domain_u: Optional[Tuple[float, float]] = None,
        domain_v: Optional[Tuple[float, float]] = None,
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
        domain_u : Tuple[float, float], optional
            U parameter minimum and maximum.
        domain_v : Tuple[float, float], optional
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
            builder = BRepBuilderAPI_MakeFace(
                surface.occ_surface, min_u, max_u, min_v, max_v, precision
            )
        elif loop:
            builder = BRepBuilderAPI_MakeFace(
                surface.occ_surface, loop.occ_wire, inside
            )
        else:
            builder = BRepBuilderAPI_MakeFace(surface.occ_surface, precision)
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
        points = []
        for vertex in self.loops[0].vertices:
            points.append(vertex.point)
        return Polygon(points)

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
        nurbs = OCCNurbsSurface()
        try:
            occ_surface = self.occ_adaptor.BSpline()
        except Exception:
            convert = GeomConvert_ApproxSurface(
                self.occ_adaptor.Surface().Surface(),
                precision,
                GeomAbs_Shape.GeomAbs_C1,
                GeomAbs_Shape.GeomAbs_C1,
                maxdegree_u,
                maxdegree_v,
                maxsegments_u,
                maxsegments_v,
            )
            occ_surface = convert.Surface()
        nurbs.occ_surface = occ_surface
        return nurbs

    def is_valid(self) -> bool:
        """
        Verify that the face is valid.

        Returns
        -------
        bool

        """
        return brepalgo_IsValid(self.occ_face)

    def fix(self) -> None:
        """
        Try to fix the face.

        Returns
        -------
        None

        """
        fixer = ShapeFix_Face(self.occ_face)
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
        builder = BRepBuilderAPI_MakeFace(self.occ_face)
        if reverse:
            builder.Add(loop.occ_wire.Reversed())  # type: ignore
        else:
            builder.Add(loop.occ_wire)
        if not builder.IsDone():
            raise Exception(builder.Error())
        self.occ_face = builder.Face()

    def add_loops(self, loops: List[OCCBrepLoop], reverse: bool = False) -> None:
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
        builder = BRepBuilderAPI_MakeFace(self.occ_face)
        for loop in loops:
            if reverse:
                builder.Add(loop.occ_wire.Reversed())  # type: ignore
            else:
                builder.Add(loop.occ_wire)
        if not builder.IsDone():
            raise Exception(builder.Error())
        self.occ_face = builder.Face()
