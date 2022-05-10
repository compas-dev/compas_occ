from typing import List, Tuple

from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.TopoDS import topods_Face
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_VERTEX
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.TopAbs import TopAbs_WIRE
from OCC.Core.TopAbs import TopAbs_Orientation
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface

# from OCC.Core.GeomAdaptor import GeomAdaptor_Surface
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepAlgo import brepalgo_IsValid
from OCC.Core.ShapeFix import ShapeFix_Face

# from OCC.Core.BRepAlgo import brepalgo_IsTopologicallyValid

from compas.geometry import Plane
from compas.geometry import Cylinder

from compas.geometry import Cone
from compas.geometry import Sphere
from compas.geometry import Torus

from compas_occ.brep import BRepVertex
from compas_occ.brep import BRepEdge
from compas_occ.brep import BRepLoop

from compas_occ.conversions import compas_plane_to_occ_plane
from compas_occ.conversions import compas_cylinder_to_occ_cylinder
from compas_occ.conversions import compas_cone_to_occ_cone
from compas_occ.conversions import compas_sphere_to_occ_sphere
from compas_occ.conversions import compas_torus_to_occ_torus

from compas.data import Data
from compas_occ.geometry import OCCSurface
from compas_occ.geometry import OCCNurbsSurface
# from compas_occ.geometry import OCCNurbsCurve


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

    # @property
    # def data(self):
    #     return {
    #         "boundary": [edge.nurbscurve.data for edge in self.loops[0].edges],
    #         "surface": self.nurbssurface.data,
    #     }

    # @data.setter
    # def data(self, data):
    #     surface = OCCNurbsSurface.from_data(data["surface"])
    #     edges = []
    #     for curvedata in data["boundary"]:
    #         curve = OCCNurbsCurve.from_data(curvedata)
    #         edges.append(BRepEdge.from_curve(curve))
    #     loop = BRepLoop.from_edges(edges)
    #     builder = BRepBuilderAPI_MakeFace(surface.occ_surface, loop.occ_wire, True)
    #     self.occ_face = builder.Face()

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def occ_face(self) -> TopoDS_Face:
        return self._occ_face

    @occ_face.setter
    def occ_face(self, face) -> None:
        self._occ_face = topods_Face(face)

    @property
    def occ_adaptor(self) -> BRepAdaptor_Surface:
        if not self._occ_adaptor:
            self._occ_adaptor = BRepAdaptor_Surface(self.occ_face)
        return self._occ_adaptor

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
    def orientation(self) -> TopAbs_Orientation:
        return self.occ_face.Orientation()

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
