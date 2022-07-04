from compas.geometry import Point
from compas.geometry import Frame
from compas.geometry import Box
from compas.geometry import Surface
from compas.datastructures import Mesh

from OCC.Core.gp import gp_Trsf
from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Vec
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.GeomAdaptor import GeomAdaptor_Surface
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BndLib import BndLib_AddSurface_Add
from OCC.Core.BndLib import BndLib_AddSurface_AddOptimal
from OCC.Core.BRep import BRep_Tool_Surface
from OCC.Core.TopoDS import topods_Face
from OCC.Core.Geom import Geom_Line
from OCC.Core.GeomAPI import GeomAPI_IntCS
from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnSurf
from OCC.Core.Bnd import Bnd_OBB
from OCC.Core.BRepBndLib import brepbndlib_AddOBB

from compas_occ.geometry.curves import OCCCurve

from compas_occ.conversions import compas_point_from_occ_point
from compas_occ.conversions import compas_point_to_occ_point
from compas_occ.conversions import compas_vector_from_occ_vector
from compas_occ.conversions import compas_frame_from_occ_ax3
from compas_occ.conversions import compas_line_to_occ_line


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
    u_degree : list[int], read-only
        The degree of the surface in the U direction.
    v_degree : list[int], read-only
        The degree of the surface in the V direction.
    u_domain : tuple[float, float], read-only
        The parameter domain of the surface in the U direction.
    v_domain : tuple[float, float], read-only
        The parameter domain of the surface in the V direction.
    is_u_periodic : bool, read-only
        Flag indicating if the surface is periodic in the U direction.
    is_v_periodic : bool, read-only
        Flag indicating if the surface is periodic in the V direction.

    Other Attributes
    ----------------
    occ_surface : ``Geom_Surface``
        The underlying OCC surface.
    occ_shape : ``TopoDS_Shape``, read-only
        An OCC face containing the surface converted to a shape.
    occ_face : ``TopoDS_Face``, read-only
        An OCC face containing the surface.

    """

    def __init__(self, name=None):
        super().__init__(name=name)
        self._occ_surface = None

    @property
    def occ_surface(self):
        return self._occ_surface

    @occ_surface.setter
    def occ_surface(self, surface):
        self._occ_surface = surface

    # ==============================================================================
    # Data
    # ==============================================================================

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_occ(cls, occ_surface):
        """Construct a NUBRS surface from an existing OCC BSplineSurface.

        Parameters
        ----------
        occ_surface : Geom_BSplineSurface
            A OCC surface.

        Returns
        -------
        :class:`OCCSurface`
            The constructed surface.

        """
        surface = cls()
        surface.occ_surface = occ_surface
        return surface

    @classmethod
    def from_face(cls, face):
        """Construct surface from an existing OCC TopoDS_Face.

        Parameters
        ----------
        face : TopoDS_Face
            An OCC face in wich the surface is embedded.

        Returns
        -------
        :class:`OCCSurface`

        """
        srf = BRep_Tool_Surface(face)
        return cls.from_occ(srf)

    # ==============================================================================
    # Conversions
    # ==============================================================================

    def to_step(self, filepath, schema="AP203"):
        """Write the surface geometry to a STP file.

        Parameters
        ----------
        filepath : str
        schema : str, optional

        Returns
        -------
        None

        """
        from OCC.Core.STEPControl import STEPControl_Writer
        from OCC.Core.STEPControl import STEPControl_AsIs
        from OCC.Core.Interface import Interface_Static_SetCVal
        from OCC.Core.IFSelect import IFSelect_RetDone

        step_writer = STEPControl_Writer()
        Interface_Static_SetCVal("write.step.schema", schema)
        step_writer.Transfer(self.occ_face, STEPControl_AsIs)
        status = step_writer.Write(filepath)
        if status != IFSelect_RetDone:
            raise AssertionError("Operation failed.")

    def to_tesselation(self):
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
    # OCC
    # ==============================================================================

    @property
    def occ_shape(self):
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace

        return BRepBuilderAPI_MakeFace(self.occ_surface, 1e-6).Shape()

    @property
    def occ_face(self):
        return topods_Face(self.occ_shape)

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def u_degree(self):
        return self.occ_surface.UDegree()

    @property
    def v_degree(self):
        return self.occ_surface.VDegree()

    @property
    def u_domain(self):
        umin, umax, _, _ = self.occ_surface.Bounds()
        return umin, umax

    @property
    def v_domain(self):
        _, _, vmin, vmax = self.occ_surface.Bounds()
        return vmin, vmax

    @property
    def is_u_periodic(self):
        return self.occ_surface.IsUPeriodic()

    @property
    def is_v_periodic(self):
        return self.occ_surface.IsVPeriodic()

    # ==============================================================================
    # Methods
    # ==============================================================================

    def copy(self):
        """Make an independent copy of the current surface.

        Returns
        -------
        :class:`compas_occ.geometry.OCCSurface`

        """
        cls = type(self)
        surface = cls()
        surface.occ_surface = self.occ_surface.Copy()
        return surface

    def transform(self, T):
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
        self.occ_surface.Transform(_T)

    def u_isocurve(self, u):
        """Compute the isoparametric curve at parameter u.

        Parameters
        ----------
        u : float

        Returns
        -------
        :class:`~compas_occ.geometry.OCCCurve`

        """
        occ_curve = self.occ_surface.UIso(u)
        return OCCCurve.from_occ(occ_curve)

    def v_isocurve(self, v):
        """Compute the isoparametric curve at parameter v.

        Parameters
        ----------
        v : float

        Returns
        -------
        :class:`~compas_occ.geometry.OCCCurve`

        """
        occ_curve = self.occ_surface.VIso(v)
        return OCCCurve.from_occ(occ_curve)

    def boundary(self):
        """Compute the boundary curves of the surface.

        Returns
        -------
        list[:class:`~compas_occ.geometry.OCCCurve`]

        """
        umin, umax, vmin, vmax = self.occ_surface.Bounds()
        curves = [
            self.v_isocurve(vmin),
            self.u_isocurve(umax),
            self.v_isocurve(vmax),
            self.u_isocurve(umin),
        ]
        curves[-2].reverse()
        curves[-1].reverse()
        return curves

    def point_at(self, u, v):
        """Compute a point on the surface.

        Parameters
        ----------
        u : float
        v : float

        Returns
        -------
        :class:`~compas.geometry.Point`

        """
        point = self.occ_surface.Value(u, v)
        return compas_point_from_occ_point(point)

    def curvature_at(self, u, v):
        """Compute the curvature at a point on the surface.

        Parameters
        ----------
        u : float
        v : float

        Returns
        -------
        :class:`~compas.geometry.Vector`

        """
        props = GeomLProp_SLProps(self.occ_surface, u, v, 2, 1e-6)
        gaussian = props.GaussianCurvature()
        mean = props.MeanCurvature()
        point = props.Value()
        normal = props.Normal()
        return (
            gaussian,
            mean,
            compas_point_from_occ_point(point),
            compas_vector_from_occ_vector(normal),
        )

    def frame_at(self, u, v):
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
        self.occ_surface.D1(u, v, point, uvec, vvec)
        return Frame(
            compas_point_from_occ_point(point),
            compas_vector_from_occ_vector(uvec),
            compas_vector_from_occ_vector(vvec),
        )

    def aabb(self, precision=0.0, optimal=False):
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
            add = BndLib_AddSurface_AddOptimal
        else:
            add = BndLib_AddSurface_Add
        add(GeomAdaptor_Surface(self.occ_surface), precision, box)
        return Box.from_diagonal(
            (
                compas_point_from_occ_point(box.CornerMin()),
                compas_point_from_occ_point(box.CornerMax()),
            )
        )

    def closest_point(self, point, return_parameters=False):
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
            compas_point_to_occ_point(), self.occ_surface
        )
        point = Point.from_occ(projector.NearestPoint())
        if not return_parameters:
            return point
        return point, projector.LowerDistanceParameters()

    def obb(self, precision=0.0):
        """Compute the oriented bounding box of the surface.

        Parameters
        ----------
        precision : float, optional

        Returns
        -------
        :class:`~compas.geometry.Box`

        """
        box = Bnd_OBB()
        brepbndlib_AddOBB(self.occ_shape, box, True, True, True)
        return Box(
            compas_frame_from_occ_ax3(box.Position()),
            box.XHSize(),
            box.YHSize(),
            box.ZHSize(),
        )

    def intersections_with_line(self, line):
        """Compute the intersections with a line.

        Parameters
        ----------
        line : :class:`~compas.geometry.Line`

        Returns
        -------
        list[:class:`~compas.geometry.Point`]

        """
        intersection = GeomAPI_IntCS(
            Geom_Line(compas_line_to_occ_line(line)), self.occ_surface
        )
        points = []
        for index in range(intersection.NbPoints()):
            pnt = intersection.Point(index + 1)
            point = compas_point_from_occ_point(pnt)
            points.append(point)
        return points
