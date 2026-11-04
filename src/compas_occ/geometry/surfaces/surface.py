import os
from typing import Literal
from typing import Optional
from typing import Self
from typing import Union
from typing import cast
from typing import overload

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

from compas._typing import CoordinateType
from compas._typing import FilePath
from compas.data import Data
from compas.geometry import Box
from compas.geometry import Curve
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
    native_surface
        The native OCC surface.
    name
        The name of the surface.

    Attributes
    ----------
    continuity
        The degree of continuity of the surface.
    degree_u
        The degree of the surface in the U direction.
    degree_v
        The degree of the surface in the V direction.
    domain_u
        The parameter domain of the surface in the U direction.
    domain_v
        The parameter domain of the surface in the V direction.
    is_periodic_u
        Flag indicating if the surface is periodic in the U direction.
    is_periodic_v
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
        face
            An OCC face in wich the surface is embedded.

        Returns
        -------
        OCCSurface

        """
        srf = BRep_Tool.Surface(face)
        return cls.from_native(srf)

    @classmethod
    def from_native(cls, surface: object) -> Self:
        """Construct a surface from an existing OCC Surface.

        Parameters
        ----------
        surface
            An OCC surface.

        Returns
        -------
        OCCSurface
            The constructed surface.

        """
        return cls(cast(Geom_Surface, surface))

    @classmethod
    def from_occ(cls, native_surface: Geom_Surface) -> "OCCSurface":
        """Construct a surface from an existing OCC Surface.

        Parameters
        ----------
        native_surface
            An OCC surface.

        Returns
        -------
        OCCSurface
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

    def to_step(self, filepath: FilePath, schema: str = "AP203") -> None:
        """Write the surface geometry to a STP file.

        Parameters
        ----------
        filepath
            The path to the output file.
        schema
            The STEP schema to use.

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
        status = step_writer.Write(os.fspath(filepath))
        if status != IFSelect_RetDone:
            raise AssertionError("Operation failed.")

    # ==============================================================================
    # Methods
    # ==============================================================================

    def copy(self, cls: type[Data] | None = None, copy_guid: bool = False) -> Self:
        """Make an independent copy of the current surface.

        Returns
        -------
        OCCSurface

        """
        surface_cls = cast(type[OCCSurface], cls or type(self))
        native_surface = self.native_surface.Copy()
        surface = surface_cls.from_native(native_surface)
        if self._name is not None:
            surface._name = self.name
        if copy_guid:
            surface._guid = self.guid
        return cast(Self, surface)

    def transform(self, transformation: Transformation) -> None:
        """Transform this surface.

        Parameters
        ----------
        transformation
            A transformation.

        Returns
        -------
        None

        """
        _T = gp_Trsf()
        _T.SetValues(*transformation.list[:12])
        self.native_surface.Transform(_T)

    def isocurve_u(self, u: float) -> OCCCurve:
        """Compute the isoparametric curve at parameter u.

        Parameters
        ----------
        u
            The parameter value.

        Returns
        -------
        OCCCurve

        """
        occ_curve = self.native_surface.UIso(u)
        return OCCCurve.from_native(occ_curve)

    def isocurve_v(self, v: float) -> OCCCurve:
        """Compute the isoparametric curve at parameter v.

        Parameters
        ----------
        v
            The parameter value.

        Returns
        -------
        OCCCurve

        """
        occ_curve = self.native_surface.VIso(v)
        return OCCCurve.from_native(occ_curve)

    def boundary(self) -> list[Union[Curve, Line]]:
        """Compute the boundary curves of the surface.

        Returns
        -------
        list[OCCCurve]

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
        return cast(list[Union[Curve, Line]], curves)

    def point_at(self, u: float, v: float) -> Point:
        """Compute a point on the surface.

        Parameters
        ----------
        u : float
        v : float

        Returns
        -------
        Point

        """
        point = self.native_surface.Value(u, v)
        return point_to_compas(point)

    def curvature_at(self, u: float, v: float) -> Vector:
        """Compute the curvature at a point on the surface.

        Parameters
        ----------
        u
            The U parameter.
        v
            The V parameter.

        Returns
        -------
        Vector

        """
        props = GeomLProp_SLProps(self.native_surface, u, v, 2, 1e-6)
        normal = props.Normal()
        return direction_to_compas(normal)

    def normal_at(self, u: float, v: float) -> Vector:
        """Compute the unit normal at surface parameters U and V.

        Parameters
        ----------
        u
            The U parameter.
        v
            The V parameter.

        Returns
        -------
        Vector
            The unit surface normal.

        """
        props = GeomLProp_SLProps(self.native_surface, u, v, 1, 1e-6)
        return direction_to_compas(props.Normal())

    def gaussian_curvature_at(self, u: float, v: float) -> float:
        """Compute the Gaussian curvature at a point on the surface.

        Parameters
        ----------
        u
            The U parameter.
        v
            The V parameter.

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
        u
            The U parameter.
        v
            The V parameter.

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
        u
            The U parameter.
        v
            The V parameter.

        Returns
        -------
        Frame

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

    @property
    def aabb(self) -> Box:
        """Compute the axis aligned bounding box of the surface."""
        box = Bnd_Box()
        BndLib_AddSurface.Add(GeomAdaptor_Surface(self.native_surface), 0.0, box)
        return Box.from_diagonal(
            (
                point_to_compas(box.CornerMin()),
                point_to_compas(box.CornerMax()),
            )
        )

    @overload
    def closest_point(self, point: CoordinateType, return_parameters: Literal[False] = False) -> Optional[Point]: ...

    @overload
    def closest_point(
        self,
        point: CoordinateType,
        return_parameters: Literal[True],
    ) -> Optional[tuple[Point, tuple[float, float]]]: ...

    def closest_point(
        self,
        point: CoordinateType,
        return_parameters: bool = False,
    ) -> Optional[Union[Point, tuple[Point, tuple[float, float]]]]:
        """Compute the closest point on the curve to a given point.

        Parameters
        ----------
        point
            The point to project to the surface.
        return_parameters
            If True, return the surface UV parameters in addition to the closest point.

        Returns
        -------
        Point | tuple[Point, tuple[float, float]] | None
            If `return_parameters` is False, the nearest point on the surface.
            If `return_parameters` is True, the UV parameters in addition to the nearest point on the surface.
            If the projection fails, `None`.

        """
        projector = GeomAPI_ProjectPointOnSurf(
            point_to_occ(cast(Point, point)),
            self.native_surface,
        )
        if projector.NbPoints() == 0:
            return None
        point = point_to_compas(projector.NearestPoint())
        if not return_parameters:
            return point
        u, v = projector.LowerDistanceParameters()
        return point, (u, v)

    @property
    def obb(self) -> Box:
        """Compute the oriented bounding box of the surface.

        Returns
        -------
        Box

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
        line
            The intersecting line.

        Returns
        -------
        list[Point]

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
        curve
            The intersecting curve.


        Returns
        -------
        list[Point]

        """
        intersection = GeomAPI_IntCS(curve.occ_curve, self.native_surface)
        points = []
        for index in range(intersection.NbPoints()):
            pnt = intersection.Point(index + 1)
            point = point_to_compas(pnt)
            points.append(point)
        return points
