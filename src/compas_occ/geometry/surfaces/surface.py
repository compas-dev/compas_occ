from typing import Optional
from typing import Union

from OCC.Core.Bnd import Bnd_Box
from OCC.Core.Bnd import Bnd_OBB
from OCC.Core.BndLib import BndLib_AddSurface
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.Geom import Geom_Line
from OCC.Core.Geom import Geom_Surface
from OCC.Core.GeomAdaptor import GeomAdaptor_Surface
from OCC.Core.GeomAPI import GeomAPI_IntCS
from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnSurf
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Trsf
from OCC.Core.gp import gp_Vec
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import topods

from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Surface
from compas.geometry import Transformation
from compas.geometry import Vector
from compas_occ.conversions import ax3_to_compas
from compas_occ.conversions import direction_to_compas
from compas_occ.conversions import line_to_occ
from compas_occ.conversions import point_to_compas
from compas_occ.conversions import point_to_occ
from compas_occ.conversions import vector_to_compas
from compas_occ.geometry import OCCCurve


class OCCSurface(Surface):
    """Class representing a general surface object.

    Parameters
    ----------
    name : str, optional
        The name of the surface.

    Attributes
    ----------
    continuity : int, read-only
        The degree of continuity of the surface.
    degree_u : list[int], read-only
        The degree of the surface in the U direction.
    degree_v : list[int], read-only
        The degree of the surface in the V direction.
    domain_u : tuple[float, float], read-only
        The parameter domain of the surface in the U direction.
    domain_v : tuple[float, float], read-only
        The parameter domain of the surface in the V direction.
    is_periodic_u : bool, read-only
        Flag indicating if the surface is periodic in the U direction.
    is_periodic_v : bool, read-only
        Flag indicating if the surface is periodic in the V direction.

    """

    _native_surface: Geom_Surface

    def __init__(self, native_surface: Geom_Surface, name: Optional[str] = None):
        super().__init__(name=name)
        self.native_surface = native_surface

    @property
    def native_surface(self) -> Geom_Surface:
        return self._native_surface

    @native_surface.setter
    def native_surface(self, surface: Geom_Surface) -> None:
        self._native_surface = surface

    @property
    def occ_surface(self) -> Geom_Surface:
        return self._native_surface

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_shape(self) -> TopoDS_Shape:
        return BRepBuilderAPI_MakeFace(self.native_surface, 1e-6).Shape()

    @property
    def occ_face(self) -> TopoDS_Face:
        return topods.Face(self.occ_shape)

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def domain_u(self) -> tuple[float, float]:
        umin, umax, _, _ = self.native_surface.Bounds()
        return umin, umax

    @property
    def domain_v(self) -> tuple[float, float]:
        _, _, vmin, vmax = self.native_surface.Bounds()
        return vmin, vmax

    @property
    def is_periodic_u(self) -> bool:
        return self.native_surface.IsUPeriodic()

    @property
    def is_periodic_v(self) -> bool:
        return self.native_surface.IsVPeriodic()

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_face(cls, face: TopoDS_Face) -> "OCCSurface":
        """Construct a surface from an existing OCC TopoDS_Face.

        Parameters
        ----------
        face : TopoDS_Face
            An OCC face in wich the surface is embedded.

        Returns
        -------
        :class:`OCCSurface`

        """
        srf = BRep_Tool.Surface(face)
        return cls.from_native(srf)

    @classmethod
    def from_native(cls, native_surface: Geom_Surface) -> "OCCSurface":
        """Construct a surface from an existing OCC Surface.

        Parameters
        ----------
        native_surface : Geom_Surface
            An OCC surface.

        Returns
        -------
        :class:`OCCSurface`
            The constructed surface.

        """
        return cls(native_surface)

    @classmethod
    def from_occ(cls, native_surface: Geom_Surface) -> "OCCSurface":
        """Construct a surface from an existing OCC Surface.

        Parameters
        ----------
        native_surface : Geom_Surface
            An OCC surface.

        Returns
        -------
        :class:`OCCSurface`
            The constructed surface.

        Warnings
        --------
        .. deprecated:: 1.3
            Use `from_native` instead

        """
        return cls(native_surface)

    # ==============================================================================
    # Conversions
    # ==============================================================================

    def to_step(self, filepath: str, schema: str = "AP203") -> None:
        """Write the surface geometry to a STP file.

        Parameters
        ----------
        filepath : str
        schema : str, optional

        Returns
        -------
        None

        """
        from OCC.Core.IFSelect import IFSelect_RetDone
        from OCC.Core.Interface import Interface_Static
        from OCC.Core.STEPControl import STEPControl_AsIs
        from OCC.Core.STEPControl import STEPControl_Writer

        step_writer = STEPControl_Writer()
        Interface_Static.SetCVal("write.step.schema", schema)
        step_writer.Transfer(self.occ_face, STEPControl_AsIs)  # type: ignore
        status = step_writer.Write(filepath)
        if status != IFSelect_RetDone:
            raise AssertionError("Operation failed.")

    def to_tesselation(self) -> Mesh:
        """Convert the surface to a triangle mesh.

        Returns
        -------
        :class:`~compas.datastructures.Mesh`

        """
        from OCC.Core.Tesselator import ShapeTesselator

        tess = ShapeTesselator(self.occ_shape)
        tess.Compute()
        vertices = []
        triangles = []
        for i in range(tess.ObjGetVertexCount()):
            vertices.append(tess.GetVertex(i))
        for i in range(tess.ObjGetTriangleCount()):
            triangles.append(tess.GetTriangleIndex(i))
        return Mesh.from_vertices_and_faces(vertices, triangles)

    # ==============================================================================
    # Methods
    # ==============================================================================

    def copy(self) -> "OCCSurface":
        """Make an independent copy of the current surface.

        Returns
        -------
        :class:`compas_occ.geometry.OCCSurface`

        """
        cls = type(self)
        native_surface = self.native_surface.Copy()
        return cls.from_native(native_surface)  # type: ignore

    def transform(self, T: Transformation) -> None:
        """Transform this surface.

        Parameters
        ----------
        T : :class:`~compas.geometry.Transformation`

        Returns
        -------
        None

        """
        _T = gp_Trsf()
        _T.SetValues(*T.list[:12])
        self.native_surface.Transform(_T)

    def isocurve_u(self, u: float) -> OCCCurve:
        """Compute the isoparametric curve at parameter u.

        Parameters
        ----------
        u : float

        Returns
        -------
        :class:`~compas_occ.geometry.OCCCurve`

        """
        occ_curve = self.native_surface.UIso(u)
        return OCCCurve.from_native(occ_curve)

    def isocurve_v(self, v: float) -> OCCCurve:
        """Compute the isoparametric curve at parameter v.

        Parameters
        ----------
        v : float

        Returns
        -------
        :class:`~compas_occ.geometry.OCCCurve`

        """
        occ_curve = self.native_surface.VIso(v)
        return OCCCurve.from_native(occ_curve)

    def boundary(self) -> list[OCCCurve]:
        """Compute the boundary curves of the surface.

        Returns
        -------
        list[:class:`~compas_occ.geometry.OCCCurve`]

        """
        umin, umax, vmin, vmax = self.native_surface.Bounds()
        curves = [
            self.isocurve_v(vmin),
            self.isocurve_u(umax),
            self.isocurve_v(vmax),
            self.isocurve_u(umin),
        ]
        curves[-2].reverse()
        curves[-1].reverse()
        return curves

    def point_at(self, u: float, v: float) -> Point:
        """Compute a point on the surface.

        Parameters
        ----------
        u : float
        v : float

        Returns
        -------
        :class:`~compas.geometry.Point`

        """
        point = self.native_surface.Value(u, v)
        return point_to_compas(point)

    def curvature_at(self, u: float, v: float) -> Vector:
        """Compute the curvature at a point on the surface.

        Parameters
        ----------
        u : float
        v : float

        Returns
        -------
        :class:`~compas.geometry.Vector`

        """
        props = GeomLProp_SLProps(self.native_surface, u, v, 2, 1e-6)
        normal = props.Normal()
        return direction_to_compas(normal)

    def gaussian_curvature_at(self, u: float, v: float) -> float:
        """Compute the Gaussian curvature at a point on the surface.

        Parameters
        ----------
        u : float
        v : float

        Returns
        -------
        float

        """
        props = GeomLProp_SLProps(self.native_surface, u, v, 2, 1e-6)
        return props.GaussianCurvature()

    def mean_curvature_at(self, u: float, v: float) -> float:
        """Compute the mean curvature at a point on the surface.

        Parameters
        ----------
        u : float
        v : float

        Returns
        -------
        float

        """
        props = GeomLProp_SLProps(self.native_surface, u, v, 2, 1e-6)
        return props.MeanCurvature()

    def frame_at(self, u: float, v: float) -> Frame:
        """Compute the local frame at a point on the curve.

        Parameters
        ----------
        u : float
        v : float

        Returns
        -------
        :class:`~compas.geometry.Frame`

        """
        point = gp_Pnt()
        uvec = gp_Vec()
        vvec = gp_Vec()
        self.native_surface.D1(u, v, point, uvec, vvec)
        return Frame(
            point_to_compas(point),
            vector_to_compas(uvec),
            vector_to_compas(vvec),
        )

    def aabb(self, precision: float = 0.0, optimal: bool = False) -> Box:
        """Compute the axis aligned bounding box of the surface.

        Parameters
        ----------
        precision : float, optional
        optimal : bool, optional

        Returns
        -------
        :class:`~compas.geometry.Box`

        """
        box = Bnd_Box()
        if optimal:
            add = BndLib_AddSurface.AddOptimal
        else:
            add = BndLib_AddSurface.Add
        add(GeomAdaptor_Surface(self.native_surface), precision, box)
        return Box.from_diagonal(
            (
                point_to_compas(box.CornerMin()),
                point_to_compas(box.CornerMax()),
            )
        )

    def closest_point(
        self,
        point: Point,
        return_parameters: bool = False,
    ) -> Union[Point, tuple[Point, tuple[float, float]]]:
        """Compute the closest point on the curve to a given point.

        Parameters
        ----------
        point : Point
            The point to project to the surface.
        return_parameters : bool, optional
            If True, return the surface UV parameters in addition to the closest point.

        Returns
        -------
        :class:`~compas.geometry.Point` | tuple[:class:`~compas.geometry.Point`, tuple[float, float]]
            If `return_parameters` is False, the nearest point on the surface.
            If `return_parameters` is True, the UV parameters in addition to the nearest point on the surface.

        """
        projector = GeomAPI_ProjectPointOnSurf(
            point_to_occ(point),
            self.native_surface,
        )
        point = point_to_compas(projector.NearestPoint())
        if not return_parameters:
            return point
        return point, projector.LowerDistanceParameters()

    def obb(self, precision: float = 0.0) -> Box:
        """Compute the oriented bounding box of the surface.

        Parameters
        ----------
        precision : float, optional

        Returns
        -------
        :class:`~compas.geometry.Box`

        """
        box = Bnd_OBB()
        brepbndlib.AddOBB(self.occ_shape, box, True, True, True)
        return Box(
            box.XHSize(),
            box.YHSize(),
            box.ZHSize(),
            frame=ax3_to_compas(box.Position()),
        )

    def intersections_with_line(self, line: Line) -> list[Point]:
        """Compute the intersections with a line.

        Parameters
        ----------
        line : :class:`~compas.geometry.Line`

        Returns
        -------
        list[:class:`~compas.geometry.Point`]

        """
        intersection = GeomAPI_IntCS(Geom_Line(line_to_occ(line)), self.native_surface)
        points = []
        for index in range(intersection.NbPoints()):
            pnt = intersection.Point(index + 1)
            point = point_to_compas(pnt)
            points.append(point)
        return points

    def intersections_with_curve(self, curve: OCCCurve) -> list[Point]:
        """Compute the intersections with a curve.

        Parameters
        ----------
        curve : :class:`compas_occ.geometry.OCCCurve`

        Returns
        -------
        list[:class:`compas.geometry.Point`]

        """
        intersection = GeomAPI_IntCS(curve.occ_curve, self.native_surface)
        points = []
        for index in range(intersection.NbPoints()):
            pnt = intersection.Point(index + 1)
            point = point_to_compas(pnt)
            points.append(point)
        return points
