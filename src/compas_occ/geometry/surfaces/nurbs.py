from compas.geometry import Point, Vector, Line, Frame, Box
from compas.utilities import flatten
from compas.datastructures import Mesh

from compas_occ.conversions import compas_line_to_occ_line
from compas_occ.conversions import compas_point_from_occ_point
from compas_occ.conversions import compas_point_to_occ_point
from compas_occ.conversions import compas_vector_from_occ_vector
from compas_occ.conversions import compas_vector_to_occ_vector
from compas_occ.conversions import compas_frame_from_occ_position
from compas_occ.conversions import array2_from_points2
from compas_occ.conversions import array1_from_floats1
from compas_occ.conversions import array2_from_floats2
from compas_occ.conversions import array1_from_integers1
from compas_occ.conversions import floats2_from_array2
from compas_occ.conversions import points2_from_array2

from ..curves import OCCNurbsCurve

try:
    from compas.geometry import NurbsSurface
except ImportError:
    from compas.geometry import Geometry as NurbsSurface

from OCC.Core.gp import gp_Trsf
from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Vec
from OCC.Core.Geom import Geom_BSplineSurface
from OCC.Core.Geom import Geom_Line
from OCC.Core.GeomAPI import GeomAPI_IntCS
from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnSurf
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.TopoDS import topods_Face
from OCC.Core.BRep import BRep_Tool_Surface
from OCC.Core.GeomFill import GeomFill_BSplineCurves
from OCC.Core.GeomFill import GeomFill_CoonsStyle
from OCC.Core.GeomAdaptor import GeomAdaptor_Surface
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.Bnd import Bnd_OBB
from OCC.Core.BndLib import BndLib_AddSurface_Add
from OCC.Core.BndLib import BndLib_AddSurface_AddOptimal
from OCC.Core.BRepBndLib import brepbndlib_AddOBB


Point.from_occ = classmethod(compas_point_from_occ_point)
Point.to_occ = compas_point_to_occ_point
Vector.from_occ = classmethod(compas_vector_from_occ_vector)
Vector.to_occ = compas_vector_to_occ_vector
Frame.from_occ = classmethod(compas_frame_from_occ_position)
Line.to_occ = compas_line_to_occ_line


class Points:
    def __init__(self, surface):
        self.occ_surface = surface

    @property
    def points(self):
        return points2_from_array2(self.occ_surface.Poles())

    def __getitem__(self, index):
        try:
            u, v = index
        except TypeError:
            return self.points[index]
        else:
            pnt = self.occ_surface.Pole(u + 1, v + 1)
            return Point.from_occ(pnt)

    def __setitem__(self, index, point):
        u, v = index
        self.occ_surface.SetPole(u + 1, v + 1, point.to_occ())

    def __len__(self):
        return self.occ_surface.NbVPoles()
        # return self.occ_surface.Poles().NbColumns()

    def __iter__(self):
        return iter(self.points)


class OCCNurbsSurface(NurbsSurface):
    """Class representing a NURBS surface based on the BSplineSurface of the OCC geometry kernel.

    Parameters
    ----------
    name : str, optional
        The name of the curve

    Examples
    --------
    Construct a surface from points...

    .. code-block:: python

        from compas.geometry import Point
        from compas_occ.geometry import OCCNurbsSurface

        points = [
            [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
            [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
            [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
            [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
        ]

        surface = OCCNurbsSurface.from_points(points=points)

    Construct a surface from points...

    .. code-block:: python

        from compas.geometry import Point
        from compas_occ.geometry import OCCNurbsSurface

        points = [
            [Point(0, 0, 0), Point(1, 0, +0), Point(2, 0, +0), Point(3, 0, +0), Point(4, 0, +0), Point(5, 0, 0)],
            [Point(0, 1, 0), Point(1, 1, -1), Point(2, 1, -1), Point(3, 1, -1), Point(4, 1, -1), Point(5, 1, 0)],
            [Point(0, 2, 0), Point(1, 2, -1), Point(2, 2, +2), Point(3, 2, +2), Point(4, 2, -1), Point(5, 2, 0)],
            [Point(0, 3, 0), Point(1, 3, -1), Point(2, 3, +2), Point(3, 3, +2), Point(4, 3, -1), Point(5, 3, 0)],
            [Point(0, 4, 0), Point(1, 4, -1), Point(2, 4, -1), Point(3, 4, -1), Point(4, 4, -1), Point(5, 4, 0)],
            [Point(0, 5, 0), Point(1, 5, +0), Point(2, 5, +0), Point(3, 5, +0), Point(4, 5, +0), Point(5, 5, 0)],
        ]

        weights = [
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        ]

        surface = OCCNurbsSurface.from_parameters(
            points=points,
            weights=weights,
            u_knots=[1.0, 1 + 1/9, 1 + 2/9, 1 + 3/9, 1 + 4/9, 1 + 5/9, 1 + 6/9, 1 + 7/9, 1 + 8/9, 2.0],
            v_knots=[0.0, 1/9, 2/9, 3/9, 4/9, 5/9, 6/9, 7/9, 8/9, 1.0],
            u_mults=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            v_mults=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            u_degree=3,
            v_degree=3,
        )

    """

    def __init__(self, name=None):
        super(OCCNurbsSurface, self).__init__(name=name)
        self.occ_surface = None  #: (:class:`compas.geometry.Point`) Reference to the underlying OCC BSpline Surface.
        self._points = None

    def __eq__(self, other):
        for a, b in zip(flatten(self.points), flatten(other.points)):
            if a != b:
                return False
        for a, b in zip(flatten(self.weights), flatten(other.weights)):
            if a != b:
                return False
        for a, b in zip(self.u_knots, self.v_knots):
            if a != b:
                return False
        for a, b in zip(self.u_mults, self.v_mults):
            if a != b:
                return False
        if self.u_degree != self.v_degree:
            return False
        if self.is_u_periodic != self.is_v_periodic:
            return False
        return True

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self):
        """:obj:`dict` - Represenation of the surface as a Python dict."""
        return {
            'points': [[point.data for point in row] for row in self.points],
            'weights': self.weights,
            'u_knots': self.u_knots,
            'v_knots': self.v_knots,
            'u_mults': self.u_mults,
            'v_mults': self.v_mults,
            'u_degree': self.u_degree,
            'v_degree': self.v_degree,
            'is_u_periodic': self.is_u_periodic,
            'is_v_periodic': self.is_v_periodic
        }

    @data.setter
    def data(self, data):
        points = [[Point.from_data(point) for point in row] for row in data['points']]
        weights = data['weights']
        u_knots = data['u_knots']
        v_knots = data['v_knots']
        u_mults = data['u_mults']
        v_mults = data['v_mults']
        u_degree = data['u_degree']
        v_degree = data['v_degree']
        is_u_periodic = data['is_u_periodic']
        is_v_periodic = data['is_v_periodic']
        self.occ_surface = Geom_BSplineSurface(
            array2_from_points2(points),
            array1_from_floats1(weights),
            array1_from_floats1(u_knots),
            array1_from_floats1(v_knots),
            array1_from_integers1(u_mults),
            array1_from_integers1(v_mults),
            u_degree,
            v_degree,
            is_u_periodic,
            is_v_periodic
        )

    @classmethod
    def from_data(cls, data):
        """Construct a BSpline surface from its data representation.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        :class:`OCCNurbsSurface`
            The constructed surface.
        """
        points = [[Point.from_data(point) for point in row] for row in data['points']]
        weights = data['weights']
        u_knots = data['u_knots']
        v_knots = data['v_knots']
        u_mults = data['u_mults']
        v_mults = data['v_mults']
        u_degree = data['u_degree']
        v_degree = data['v_degree']
        is_u_periodic = data['is_u_periodic']
        is_v_periodic = data['is_v_periodic']
        return NurbsSurface.from_parameters(
            points,
            weights,
            u_knots, v_knots,
            u_mults, v_mults,
            u_degree, v_degree,
            is_u_periodic, is_v_periodic
        )

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
        :class:`OCCNurbsSurface`
            The constructed surface.
        """
        surface = cls()
        surface.occ_surface = occ_surface
        return surface

    @classmethod
    def from_parameters(cls, points, weights, u_knots, v_knots, u_mults, v_mults, u_degree, v_degree, is_u_periodic=False, is_v_periodic=False):
        """Construct a NURBS surface from explicit parameters.

        Parameters
        ----------
        points : List[List[:class:`compas.geometry.Point`]]
            The control points of the surface.
        weights : List[List[:obj:`float`]]
            The weights of the control points.
        u_knots : List[:obj:`float`]
            The knots in the U direction, without multiplicities.
        v_knots : List[:obj:`float`]
            The knots in the V direction, without multiplicities.
        u_mults : List[:obj:`int`]
            The multiplicities of the knots in the U direction.
        v_mults : List[:obj:`int`]
            The multiplicities of the knots in the V direction.
        u_dergee : :obj:`int`
            Degree in the U direction.
        v_degree : :obj:`int`
            Degree in the V direction.
        is_u_periodic : :obj:`bool`, optional
            Flag indicating that the surface is periodic in the U direction.
        is_v_periodic : :obj:`bool`, optional
            Flag indicating that the surface is periodic in the V direction.

        Returns
        -------
        :class:`OCCNurbsSurface`
        """
        surface = cls()
        surface.occ_surface = Geom_BSplineSurface(
            array2_from_points2(points),
            array2_from_floats2(weights),
            array1_from_floats1(u_knots),
            array1_from_floats1(v_knots),
            array1_from_integers1(u_mults),
            array1_from_integers1(v_mults),
            u_degree,
            v_degree,
            is_u_periodic,
            is_v_periodic
        )
        return surface

    @classmethod
    def from_points(cls, points, u_degree=3, v_degree=3):
        """Construct a NURBS surface from control points.

        Parameters
        ----------
        points : List[List[:class:`compas.geometry.Point`]]
            The control points.
        u_degree : int, optional
        v_degree : int, optional

        Returns
        -------
        :class:`OCCNurbsSurface`
        """
        u = len(points[0])
        v = len(points)
        weights = [[1.0 for _ in range(u)] for _ in range(v)]
        u_degree = u_degree if u > u_degree else u - 1
        v_degree = v_degree if v > v_degree else v - 1
        u_order = u_degree + 1
        v_order = v_degree + 1
        x = u - u_order
        u_knots = [float(i) for i in range(2 + x)]
        u_mults = [u_order]
        for _ in range(x):
            u_mults.append(1)
        u_mults.append(u_order)
        x = v - v_order
        v_knots = [float(i) for i in range(2 + x)]
        v_mults = [v_order]
        for _ in range(x):
            v_mults.append(1)
        v_mults.append(v_order)
        is_u_periodic = False
        is_v_periodic = False
        return cls.from_parameters(
            points,
            weights,
            u_knots, v_knots,
            u_mults, v_mults,
            u_degree, v_degree,
            is_u_periodic, is_v_periodic
        )

    @classmethod
    def from_step(cls, filepath):
        """Load a NURBS surface from a STP file.

        Parameters
        ----------
        filepath : str

        Returns
        -------
        :class:`OCCNurbsSurface`
        """
        raise NotImplementedError

    @classmethod
    def from_face(cls, face):
        """Construct a NURBS surface from an existing OCC TopoDS_Face.

        Parameters
        ----------
        face : TopoDS_Face
            An OCC face in wich the surface is embedded.

        Returns
        -------
        :class:`OCCNurbsSurface`
        """
        srf = BRep_Tool_Surface(face)
        return cls.from_occ(srf)

    @classmethod
    def from_fill(cls, curve1, curve2):
        """Construct a NURBS surface from the infill between two NURBS curves.

        Parameters
        ----------
        curve1 : :class:`compas.geometry.NurbsCurve`
        curve2 : :class:`compas.geometry.NurbsCurve`

        Returns
        -------
        :class:`OCCNurbsSurface`
        """
        surface = cls()
        occ_fill = GeomFill_BSplineCurves(curve1.occ_curve, curve2.occ_curve, GeomFill_CoonsStyle)
        surface.occ_surface = occ_fill.Surface()
        return surface

    # ==============================================================================
    # Conversions
    # ==============================================================================

    def to_step(self, filepath, schema="AP203"):
        """Write the surface geometry to a STP file.

        Parameters
        ----------
        filepath : str
        schema : str, optional
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
        :class:`compas.datastructures.Mesh`
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
        """TopoDS_Shape - An OCC face containing the surface converted to a shape."""
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
        return BRepBuilderAPI_MakeFace(self.occ_surface, 1e-6).Shape()

    @property
    def occ_face(self):
        """TopoDS_Face - An OCC face containing the surface."""
        return topods_Face(self.occ_shape)

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def points(self):
        """List[List[:class:`compas.geometry.Point`]] - The control points of the surface."""
        if not self._points:
            self._points = Points(self.occ_surface)
        return self._points

    @property
    def weights(self):
        """List[List[:obj:`float`]] - The weights of the control points of the surface."""
        weights = self.occ_surface.Weights()
        if not weights:
            weights = [[1.0] * len(self.points[0]) for _ in range(len(self.points))]
        else:
            weights = floats2_from_array2(weights)
        return weights

    @property
    def u_knots(self):
        """List[:obj:`float`] - The knots of the surface in the U direction, without multiplicities."""
        return list(self.occ_surface.UKnots())

    @property
    def v_knots(self):
        """List[:obj:`float`] - The knots of the surface in the V direction, without multiplicities."""
        return list(self.occ_surface.VKnots())

    @property
    def u_mults(self):
        """List[:obj:`int`] - The multiplicities of the knots of the surface in the U direction."""
        return list(self.occ_surface.UMultiplicities())

    @property
    def v_mults(self):
        """List[:obj:`int`] - The multiplicities of the knots of the surface in the V direction."""
        return list(self.occ_surface.VMultiplicities())

    @property
    def u_degree(self):
        """List[:obj:`int`] - The degree of the surface in the U direction."""
        return self.occ_surface.UDegree()

    @property
    def v_degree(self):
        """List[:obj:`int`] - The degree of the surface in the V direction."""
        return self.occ_surface.VDegree()

    @property
    def u_domain(self):
        """(:obj:`float`, :obj:`float`) - The parameter domain of the surface in the U direction."""
        umin, umax, _, _ = self.occ_surface.Bounds()
        return umin, umax

    @property
    def v_domain(self):
        """(:obj:`float`, :obj:`float`) - The parameter domain of the surface in the V direction."""
        _, _, vmin, vmax = self.occ_surface.Bounds()
        return vmin, vmax

    @property
    def is_u_periodic(self):
        """:obj:`bool` - Flag indicating if the surface is periodic in the U direction."""
        return self.occ_surface.IsUPeriodic()

    @property
    def is_v_periodic(self):
        """:obj:`bool` - Flag indicating if the surface is periodic in the V direction."""
        return self.occ_surface.IsVPeriodic()

    # ==============================================================================
    # Methods
    # ==============================================================================

    def transform(self, T):
        """Transform this surface.

        Parameters
        ----------
        T : :class:`compas.geometry.Transformation`

        Returns
        -------
        None
        """
        _T = gp_Trsf()
        _T.SetValues(* T.list[:12])
        self.occ_surface.Transform(_T)

    def u_isocurve(self, u):
        """Compute the isoparametric curve at parameter u.

        Parameters
        ----------
        u : float

        Returns
        -------
        :class:`compas.geometry.NurbsCurve`
        """
        occ_curve = self.occ_surface.UIso(u)
        return OCCNurbsCurve.from_occ(occ_curve)

    def v_isocurve(self, v):
        """Compute the isoparametric curve at parameter v.

        Parameters
        ----------
        v : float

        Returns
        -------
        :class:`compas.geometry.NurbsCurve`
        """
        occ_curve = self.occ_surface.VIso(v)
        return OCCNurbsCurve.from_occ(occ_curve)

    def boundary(self):
        """Compute the boundary curves of the surface.

        Returns
        -------
        List[:class:`compas.geometry.NurbsCurve`]
        """
        umin, umax, vmin, vmax = self.occ_surface.Bounds()
        curves = [
            self.v_isocurve(vmin),
            self.u_isocurve(umax),
            self.v_isocurve(vmax),
            self.u_isocurve(umin)
        ]
        curves[-2].reverse()
        curves[-1].reverse()
        return curves

    def point_at(self, u, v):
        """Compute a point on the surface.

        Parameters
        ----------
        u : :obj:`float`
        v : :obj:`float`

        Returns
        -------
        :class:`compas.geometry.Point`
        """
        point = self.occ_surface.Value(u, v)
        return Point.from_occ(point)

    def curvature_at(self, u, v):
        """Compute the curvature at a point on the surface.

        Parameters
        ----------
        u : :obj:`float`
        v : :obj:`float`

        Returns
        -------
        :class:`compas.geometry.Vector`
        """
        props = GeomLProp_SLProps(self.occ_surface, u, v, 2, 1e-6)
        gaussian = props.GaussianCurvature()
        mean = props.MeanCurvature()
        point = props.Value()
        normal = props.Normal()
        return gaussian, mean, Point.from_occ(point), Vector.from_occ(normal)

    def frame_at(self, u, v):
        """Compute the local frame at a point on the curve.

        Parameters
        ----------
        u : :obj:`float`
        v : :obj:`float`

        Returns
        -------
        :class:`compas.geometry.Frame`
        """
        point = gp_Pnt()
        uvec = gp_Vec()
        vvec = gp_Vec()
        self.occ_surface.D1(u, v, point, uvec, vvec)
        return Frame(Point.from_occ(point), Vector.from_occ(uvec), Vector.from_occ(vvec))

    def closest_point(self, point, return_parameters=False):
        """Compute the closest point on the curve to a given point.

        Parameters
        ----------
        point : Point
            The point to project to the surface.
        return_parameters : bool, optional
            Return the projected point as well as the surface UV parameters as tuple.

        Returns
        -------
        :class:`compas.geometry.Point`
            The nearest point on the surface, if ``return_parameters`` is false.
        (:class:`compas.geometry.Point`, (float, float))
            The nearest as (point, parameters) tuple, if ``return_parameters`` is true.
        """
        projector = GeomAPI_ProjectPointOnSurf(point.to_occ(), self.occ_surface)
        point = Point.from_occ(projector.NearestPoint())
        if not return_parameters:
            return point
        return point, projector.LowerDistanceParameters()

    def aabb(self, precision=0.0, optimal=False):
        """Compute the axis aligned bounding box of the surface."""
        box = Bnd_Box()
        if optimal:
            add = BndLib_AddSurface_AddOptimal
        else:
            add = BndLib_AddSurface_Add
        add(GeomAdaptor_Surface(self.occ_surface), precision, box)
        return Box.from_diagonal((
            Point.from_occ(box.CornerMin()),
            Point.from_occ(box.CornerMax())
        ))

    def obb(self, precision=0.0):
        """Compute the oriented bounding box of the surface."""
        box = Bnd_OBB()
        brepbndlib_AddOBB(self.occ_shape, box, True, True, True)
        return Box(Frame.from_occ(box.Position()), box.XHSize(), box.YHSize(), box.ZHSize())

    def intersections_with_line(self, line):
        """Compute the intersections with a line."""
        intersection = GeomAPI_IntCS(Geom_Line(line.to_occ()), self.occ_surface)
        points = []
        for index in range(intersection.NbPoints()):
            pnt = intersection.Point(index + 1)
            point = Point.from_occ(pnt)
            points.append(point)
        return points
