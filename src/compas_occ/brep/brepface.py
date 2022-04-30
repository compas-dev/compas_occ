from typing import List

from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.TopoDS import topods_Face
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_VERTEX
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.TopAbs import TopAbs_WIRE
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAdaptor import GeomAdaptor_Surface
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace

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

from compas_occ.geometry import OCCSurface


class BRepFace:
    """Class representing a face in the BRep of a geometric shape.

    Parameters
    ----------
    face : ``TopoDS_Face``
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
    face : ``TopoDS_Face``
        The OCC BRep face.
    adaptor : ``BRepAdaptor_Surface``
        Adaptor for extracting surface geometry from the BRep face.

    """

    def __init__(self, face: TopoDS_Face):
        self._face = None
        self._adaptor = None
        self._surface = None
        self.face = face

    @property
    def face(self) -> TopoDS_Face:
        return self._face

    @face.setter
    def face(self, face) -> None:
        self._face = topods_Face(face)

    @property
    def vertices(self) -> List[BRepVertex]:
        vertices = []
        explorer = TopExp_Explorer(self.shape, TopAbs_VERTEX)
        while explorer.More():
            vertex = explorer.Current()
            vertices.append(BRepVertex(vertex))
            explorer.Next()
        return vertices

    @property
    def edges(self) -> List[BRepEdge]:
        edges = []
        explorer = TopExp_Explorer(self.shape, TopAbs_EDGE)
        while explorer.More():
            edge = explorer.Current()
            edges.append(BRepEdge(edge))
            explorer.Next()
        return edges

    @property
    def loops(self) -> List[BRepLoop]:
        loops = []
        explorer = TopExp_Explorer(self.shape, TopAbs_WIRE)
        while explorer.More():
            wire = explorer.Current()
            loops.append(BRepLoop(wire))
            explorer.Next()
        return loops

    @property
    def adaptor(self) -> BRepAdaptor_Surface:
        if not self._adaptor:
            self._adaptor = BRepAdaptor_Surface(self.face)
        return self._adaptor

    @property
    def surface(self) -> GeomAdaptor_Surface:
        if not self._surface:
            self._surface = self.adaptor.Surface()
        return self._surface

    @classmethod
    def from_plane(
        cls, plane: Plane, loop: BRepLoop = None, inside: bool = True
    ) -> "BRepFace":
        """Construct a face from a plane.

        Parameters
        ----------
        plane : :class:`compas.geometry.Plane`
            The plane.
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
                compas_plane_to_occ_plane(plane), loop.loop, inside
            )
        else:
            builder = BRepBuilderAPI_MakeFace(compas_plane_to_occ_plane(plane))
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
                compas_cylinder_to_occ_cylinder(cylinder), loop.loop, inside
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
                compas_cone_to_occ_cone(cone), loop.loop, inside
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
                compas_sphere_to_occ_sphere(sphere), loop.loop, inside
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
                compas_torus_to_occ_torus(torus), loop.loop, inside
            )
        else:
            builder = BRepBuilderAPI_MakeFace(compas_torus_to_occ_torus(torus))
        return cls(builder.Face())

    @classmethod
    def from_surface(
        cls,
        surface: OCCSurface,
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
        if loop:
            builder = BRepBuilderAPI_MakeFace(surface.occ_surface, loop.loop, inside)
        else:
            builder = BRepBuilderAPI_MakeFace(surface.occ_surface, precision)
        return cls(builder.Face())
