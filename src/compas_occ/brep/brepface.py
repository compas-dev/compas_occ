from typing import List, Tuple
from enum import Enum

from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.TopoDS import topods_Face
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_VERTEX
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.TopAbs import TopAbs_WIRE
from OCC.Core.TopAbs import TopAbs_Orientation
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepAlgo import brepalgo_IsValid
from OCC.Core.BRepGProp import brepgprop_VolumeProperties
from OCC.Core.BRepGProp import brepgprop_SurfaceProperties
from OCC.Core.ShapeFix import ShapeFix_Face
from OCC.Core.GProp import GProp_GProps
from OCC.Core.GeomConvert import GeomConvert_ApproxSurface
from OCC.Core.GeomAbs import GeomAbs_Shape

import compas.geometry
from compas.data import Data
from compas.geometry import Plane
from compas.geometry import Cylinder
from compas.geometry import Cone
from compas.geometry import Sphere
from compas.geometry import Torus

from compas_occ.brep import BRepVertex
from compas_occ.brep import BRepEdge
from compas_occ.brep import BRepLoop
from compas_occ.conversions import compas_point_from_occ_point
from compas_occ.conversions import compas_plane_to_occ_plane
from compas_occ.conversions import compas_plane_from_occ_plane
from compas_occ.conversions import compas_cylinder_to_occ_cylinder
from compas_occ.conversions import compas_cylinder_from_occ_cylinder
from compas_occ.conversions import compas_cone_to_occ_cone
from compas_occ.conversions import compas_sphere_to_occ_sphere
from compas_occ.conversions import compas_torus_to_occ_torus
from compas_occ.geometry import OCCSurface
from compas_occ.geometry import OCCNurbsSurface


class BRepFace(Data):
    """Class representing a face in the BRep of a geometric shape.

    Parameters
    ----------
    occ_face : ``TopoDS_Face``
        An OCC BRep face.

    Attributes
    ----------
    vertices : list[:class:`~compas_occ.brep.BRepVertex`], read-only
        List of BRep vertices.
    edges : list[:class:`~compas_occ.brep.BRepEdge`], read-only
        List of BRep edges.
    loops : list[:class:`~compas_occ.brep.BRepLoop`], read-only
        List of BRep loops.
    surface : ``GeomAdaptor_Surface``
        Surface geometry from the adaptor.

    Other Attributes
    ----------------
    occ_face : ``TopoDS_Face``
        The OCC BRep face.
    occ_adaptor : ``BRepAdaptor_Surface``
        Adaptor for extracting surface geometry from the BRep face.

    """

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

    def __init__(self, occ_face: TopoDS_Face = None):
        super().__init__()
        self.precision = 1e-6
        self._surface = None
        self._nurbssurface = None
        self._occ_face = None
        self._occ_adaptor = None
        if occ_face:
            self.occ_face = occ_face

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self):
        boundary = self.loops[0].data
        holes = [loop.data for loop in self.loops[1:]]

        if self.is_bspline:
            surface = self.nurbssurface
            surfacedata = {
                "type": "nurbs",
                "value": surface.data,
            }
        else:
            try:
                convert = GeomConvert_ApproxSurface(
                    self.surface,
                    1e-3,
                    GeomAbs_Shape.GeomAbs_C1,
                    GeomAbs_Shape.GeomAbs_C1,
                    5,
                    5,
                    1,
                    1,
                )
                surface = OCCNurbsSurface()
                surface.occ_surface = convert.Surface()
                surfacedata = {
                    "type": "nurbs",
                    "value": surface.data,
                }
            except Exception:
                if self.is_plane:
                    plane = compas_plane_from_occ_plane(self.occ_adaptor.Plane())
                    surfacedata = {
                        "type": "plane",
                        "value": plane.data,
                    }
                elif self.is_cylinder:
                    cylinder = compas_cylinder_from_occ_cylinder(
                        self.occ_adaptor.Cylinder()
                    )
                    surfacedata = {
                        "type": "cylinder",
                        "value": cylinder.data,
                    }
                elif self.is_cone:
                    raise NotImplementedError
                elif self.is_sphere:
                    raise NotImplementedError
                elif self.is_torus:
                    raise NotImplementedError
                else:
                    raise

        return {
            "boundary": boundary,
            "surface": surfacedata,
            "holes": holes,
        }

    @data.setter
    def data(self, data):
        loop = BRepLoop.from_data(data["boundary"])
        for hole in data["holes"]:
            pass

        if data["surface"]["type"] == "nurbs":
            surface = OCCNurbsSurface.from_data(data["surface"]["value"])
            face = BRepFace.from_surface(surface, loop=loop)
        elif data["surface"]["type"] == "plane":
            plane = Plane.from_data(data["surface"]["value"])
            face = BRepFace.from_plane(plane, loop=loop)
        elif data["surface"]["type"] == "cylinder":
            cylinder = Cylinder.from_data(data["surface"]["value"])
            face = BRepFace.from_cylinder(cylinder, loop=loop)
        else:
            raise NotImplementedError

        self.occ_face = face.occ_face

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
        self._occ_face = topods_Face(face)

    @property
    def occ_adaptor(self) -> BRepAdaptor_Surface:
        if not self._occ_adaptor:
            self._occ_adaptor = BRepAdaptor_Surface(self.occ_face)
        return self._occ_adaptor

    @property
    def orientation(self) -> TopAbs_Orientation:
        return self.occ_face.Orientation()

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def type(self) -> int:
        return BRepFace.SurfaceType(self.occ_adaptor.GetType())

    @property
    def is_plane(self) -> bool:
        return self.type == BRepFace.SurfaceType.Plane

    @property
    def is_cylinder(self) -> bool:
        return self.type == BRepFace.SurfaceType.Cylinder

    @property
    def is_sphere(self) -> bool:
        return self.type == BRepFace.SurfaceType.Sphere

    @property
    def is_torus(self) -> bool:
        return self.type == BRepFace.SurfaceType.Torus

    @property
    def is_cone(self) -> bool:
        return self.type == BRepFace.SurfaceType.Cone

    @property
    def is_bspline(self) -> bool:
        return self.type == BRepFace.SurfaceType.BSplineSurface

    @property
    def vertices(self) -> List[BRepVertex]:
        vertices = []
        explorer = TopExp_Explorer(self.occ_face, TopAbs_VERTEX)
        while explorer.More():
            vertex = explorer.Current()
            vertices.append(BRepVertex(vertex))
            explorer.Next()
        return vertices

    @property
    def edges(self) -> List[BRepEdge]:
        edges = []
        explorer = TopExp_Explorer(self.occ_face, TopAbs_EDGE)
        while explorer.More():
            edge = explorer.Current()
            edges.append(BRepEdge(edge))
            explorer.Next()
        return edges

    @property
    def loops(self) -> List[BRepLoop]:
        loops = []
        explorer = TopExp_Explorer(self.occ_face, TopAbs_WIRE)
        while explorer.More():
            wire = explorer.Current()
            loops.append(BRepLoop(wire))
            explorer.Next()
        return loops

    @property
    def surface(self) -> OCCSurface:
        if not self._surface:
            self._surface = OCCSurface()
            self._surface.occ_surface = self.occ_adaptor.Surface()
        return self._surface

    @property
    def nurbssurface(self) -> OCCNurbsSurface:
        if not self._nurbssurface:
            self._nurbssurface = OCCNurbsSurface()
            self._nurbssurface.occ_surface = self.occ_adaptor.BSpline()
        return self._nurbssurface

    @property
    def area(self) -> float:
        props = GProp_GProps()
        brepgprop_SurfaceProperties(self.occ_shape, props)
        return props.Mass()

    @property
    def centroid(self) -> compas.geometry.Point:
        props = GProp_GProps()
        brepgprop_VolumeProperties(self.occ_shape, props)
        pnt = props.CentreOfMass()
        return compas_point_from_occ_point(pnt)

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_plane(
        cls,
        plane: Plane,
        udomain: Tuple[float, float] = None,
        vdomain: Tuple[float, float] = None,
        loop: BRepLoop = None,
        inside: bool = True,
    ) -> "BRepFace":
        """Construct a face from a plane.

        Parameters
        ----------
        plane : :class:`compas.geometry.Plane`
            The plane.
        udomain : Tuple[float, float], optional
            U parameter minimum and maximum.
        vdomain : Tuple[float, float], optional
            V parameter minimum and maximum.
        loop : :class:`compas_occ.brep.BRepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`BRepFace`

        """
        plane = compas_plane_to_occ_plane(plane)
        if udomain and vdomain:
            umin, umax = udomain
            vmin, vmax = vdomain
            builder = BRepBuilderAPI_MakeFace(plane, umin, umax, vmin, vmax)
        elif loop:
            builder = BRepBuilderAPI_MakeFace(plane, loop.occ_wire, inside)
        else:
            builder = BRepBuilderAPI_MakeFace(plane)
        return cls(builder.Face())

    @classmethod
    def from_cylinder(
        cls, cylinder: Cylinder, loop: BRepLoop = None, inside: bool = True
    ) -> "BRepFace":
        """Construct a face from a cylinder.

        Parameters
        ----------
        cylinder : :class:`compas.geometry.Cylinder`
            The cylinder.
        loop : :class:`compas_occ.brep.BRepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`BRepFace`

        """
        if loop:
            builder = BRepBuilderAPI_MakeFace(
                compas_cylinder_to_occ_cylinder(cylinder), loop.occ_wire, inside
            )
        else:
            builder = BRepBuilderAPI_MakeFace(compas_cylinder_to_occ_cylinder(cylinder))
        return cls(builder.Face())

    @classmethod
    def from_cone(
        cls, cone: Cone, loop: BRepLoop = None, inside: bool = True
    ) -> "BRepFace":
        """Construct a face from a cone.

        Parameters
        ----------
        cone : :class:`compas.geometry.Cone`
            The cone.
        loop : :class:`compas_occ.brep.BRepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`BRepFace`

        """
        if loop:
            builder = BRepBuilderAPI_MakeFace(
                compas_cone_to_occ_cone(cone), loop.occ_wire, inside
            )
        else:
            builder = BRepBuilderAPI_MakeFace(compas_cone_to_occ_cone(cone))
        return cls(builder.Face())

    @classmethod
    def from_sphere(
        cls, sphere: Sphere, loop: BRepLoop = None, inside: bool = True
    ) -> "BRepFace":
        """Construct a face from a sphere.

        Parameters
        ----------
        sphere : :class:`compas.geometry.Sphere`
            The sphere.
        loop : :class:`compas_occ.brep.BRepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`BRepFace`

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
        cls, torus: Torus, loop: BRepLoop = None, inside: bool = True
    ) -> "BRepFace":
        """Construct a face from a torus.

        Parameters
        ----------
        torus : :class:`compas.geometry.Torus`
            The torus.
        loop : :class:`compas_occ.brep.BRepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`BRepFace`

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
        udomain: Tuple[float, float] = None,
        vdomain: Tuple[float, float] = None,
        precision: float = 1e-6,
        loop: BRepLoop = None,
        inside: bool = True,
    ) -> "BRepFace":
        """Construct a face from a surface.

        Parameters
        ----------
        surface : :class:`compas_occ.geometry.OCCSurface`
            The torus.
        precision : float, optional
            Precision for face construction.
        loop : :class:`compas_occ.brep.BRepLoop`, optional
            A boundary loop.
        inside : bool, optional
            If True, the face is inside the boundary loop.

        Returns
        -------
        :class:`BRepFace`

        """
        if udomain and vdomain:
            umin, umax = udomain
            vmin, vmax = vdomain
            builder = BRepBuilderAPI_MakeFace(
                surface.occ_surface, umin, umax, vmin, vmax, precision
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

    # ==============================================================================
    # Methods
    # ==============================================================================

    def is_valid(self) -> bool:
        """Verify that the face is valid.

        Returns
        -------
        bool

        """
        return brepalgo_IsValid(self.occ_face)

    def fix(self) -> None:
        """Try to fix the face.

        Returns
        -------
        None

        """
        fixer = ShapeFix_Face(self.occ_face)
        fixer.Perform()
        self.occ_face = fixer.Face()

    def add_loop(self, loop: BRepLoop, reverse: bool = False) -> None:
        """Add an inner loop to the face.

        Parameters
        ----------
        loop : :class:`compas_occ.brep.BRepLoop`
            The additional loop.

        Returns
        -------
        None

        """
        builder = BRepBuilderAPI_MakeFace(self.occ_face)
        if reverse:
            builder.Add(loop.occ_wire.Reversed())
        else:
            builder.Add(loop.occ_wire)
        if not builder.IsDone():
            raise Exception(builder.Error())
        self.occ_face = builder.Face()

    def add_loops(self, loops: List[BRepLoop], reverse: bool = False) -> None:
        """Add an inner loop to the face.

        Parameters
        ----------
        loops : list[:class:`compas_occ.brep.BRepLoop`]
            The additional loops.

        Returns
        -------
        None

        """
        builder = BRepBuilderAPI_MakeFace(self.occ_face)
        for loop in loops:
            if reverse:
                builder.Add(loop.occ_wire.Reversed())
            else:
                builder.Add(loop.occ_wire)
        if not builder.IsDone():
            raise Exception(builder.Error())
        self.occ_face = builder.Face()
