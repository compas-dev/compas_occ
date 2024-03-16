from typing import Optional
from typing import Tuple
from typing import Type

from compas.geometry import Bezier
from compas.geometry import Circle
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import Ellipse
from compas.geometry import Frame
from compas.geometry import Hyperbola
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import Parabola
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Sphere
from compas.geometry import Torus
from compas.geometry import Transformation
from compas.geometry import Vector
from OCC.Core.Geom import Geom_BezierCurve
from OCC.Core.Geom import Geom_BSplineCurve
from OCC.Core.gp import gp_Ax1
from OCC.Core.gp import gp_Ax2
from OCC.Core.gp import gp_Ax3
from OCC.Core.gp import gp_Circ
from OCC.Core.gp import gp_Cone
from OCC.Core.gp import gp_Cylinder
from OCC.Core.gp import gp_Dir
from OCC.Core.gp import gp_Elips
from OCC.Core.gp import gp_Hypr
from OCC.Core.gp import gp_Lin
from OCC.Core.gp import gp_Parab
from OCC.Core.gp import gp_Pln
from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Pnt2d
from OCC.Core.gp import gp_Sphere
from OCC.Core.gp import gp_Torus
from OCC.Core.gp import gp_Vec
from OCC.Core.gp import gp_Vec2d
from OCC.Core.TopLoc import TopLoc_Location

# =============================================================================
# To OCC
# =============================================================================


def point_to_occ(point: Point) -> gp_Pnt:
    """Convert a COMPAS point to an OCC point.

    Parameters
    ----------
    point : :class:`~compas.geometry.Point`
        The COMPAS point to convert.

    Returns
    -------
    ``gp_Pnt``

    Examples
    --------
    >>> from compas.geometry import Point
    >>> from compas_occ.conversions import point_to_occ
    >>> point = Point(0, 0, 0)
    >>> point_to_occ(point)
    <class 'gp_Pnt'>

    """
    return gp_Pnt(*point)


def vector_to_occ(vector: Vector) -> gp_Vec:
    """Convert a COMPAS vector to an OCC vector.

    Parameters
    ----------
    vector : :class:`~compas.geometry.Vector`
        The COMPAS vector to convert.

    Returns
    -------
    ``gp_Vec``

    See Also
    --------
    :func:`direction_to_occ`

    Examples
    --------
    >>> from compas.geometry import Vector
    >>> from compas_occ.conversions import vector_to_occ
    >>> vector = Vector(1, 0, 0)
    >>> vector_to_occ(vector)
    <class 'gp_Vec'>

    """
    return gp_Vec(*vector)


def direction_to_occ(vector: Vector) -> gp_Dir:
    """Convert a COMPAS vector to an OCC direction.

    Parameters
    ----------
    vector : :class:`~compas.geometry.Vector`
        The COMPAS vector to convert.

    Returns
    -------
    ``gp_Dir``

    See Also
    --------
    :func:`vector_to_occ`

    Examples
    --------
    >>> from compas.geometry import Vector
    >>> from compas_occ.conversions import direction_to_occ
    >>> vector = Vector(1, 0, 0)
    >>> direction_to_occ(vector)
    <class 'gp_Dir'>

    """
    return gp_Dir(*vector)


def axis_to_occ(axis: Tuple[Point, Vector]) -> gp_Ax1:
    """Convert a COMPAS point and vector to an OCC axis.

    Parameters
    ----------
    axis : tuple[:class:`~compas.geometry.Point`, :class:`~compas.geometry.Vector`]
        A point and vector representing an axis.

    Returns
    -------
    ``gp_Ax1``

    See Also
    --------
    :func:`line_to_occ`

    Examples
    --------
    >>> from compas.geometry import Point, Vector
    >>> from compas_occ.conversions import axis_to_occ
    >>> point = Point(0, 0, 0)
    >>> vector = Vector(1, 0, 0)
    >>> axis_to_occ((point, vector))
    <class 'gp_Ax1'>

    """
    return gp_Ax1(
        point_to_occ(axis[0]),
        direction_to_occ(axis[1]),
    )


def line_to_occ(line: Line) -> gp_Lin:
    """Convert a COMPAS line to an OCC line.

    Parameters
    ----------
    line : :class:`~compas.geometry.Line`
        The COMPAS line to convert.

    Returns
    -------
    ``gp_Lin``

    See Also
    --------
    :func:`axis_to_occ`

    Examples
    --------
    >>> from compas.geometry import Line
    >>> from compas_occ.conversions import line_to_occ
    >>> line = Line([0, 0, 0], [1, 0, 0])
    >>> line_to_occ(line)
    <class 'gp_Lin'>

    """
    return gp_Lin(
        point_to_occ(line.start),
        direction_to_occ(line.direction),
    )


def plane_to_occ(plane: Plane) -> gp_Pln:
    """Convert a COMPAS plane to an OCC plane.

    Parameters
    ----------
    plane : :class:`compas.geometry.Plane`
        The COMPAS plane.

    Returns
    -------
    ``gp_Pln``

    See Also
    --------
    :func:`plane_to_occ_ax2`
    :func:`plane_to_occ_ax3`

    Examples
    --------
    >>> from compas.geometry import Plane
    >>> from compas_occ.conversions import plane_to_occ
    >>> plane = Plane([0, 0, 0], [0, 0, 1])
    >>> plane_to_occ(plane)
    <class 'gp_Pln'>

    """
    return gp_Pln(
        point_to_occ(plane.point),
        direction_to_occ(plane.normal),
    )


def plane_to_occ_ax2(plane: Plane) -> gp_Ax2:
    """Convert a COMPAS plane to a right-handed OCC coordinate system.

    Parameters
    ----------
    plane : :class:`compas.geometry.Plane`
        The COMPAS plane.

    Returns
    -------
    ``gp_Ax2``

    See Also
    --------
    :func:`plane_to_occ`
    :func:`plane_to_occ_ax3`

    Examples
    --------
    >>> from compas.geometry import Plane
    >>> from compas_occ.conversions import plane_to_occ_ax2
    >>> plane = Plane([0, 0, 0], [0, 0, 1])
    >>> plane_to_occ_ax2(plane)
    <class 'gp_Ax2'>

    """
    return gp_Ax2(
        point_to_occ(plane.point),
        direction_to_occ(plane.normal),
    )


def plane_to_occ_ax3(plane: Plane) -> gp_Ax3:
    """Convert a COMPAS plane to a right-handed OCC coordinate system.

    Parameters
    ----------
    plane : :class:`compas.geometry.Plane`
        The COMPAS plane.

    Returns
    -------
    ``gp_Ax3``

    See Also
    --------
    :func:`plane_to_occ`
    :func:`plane_to_occ_ax2`

    Examples
    --------
    >>> from compas.geometry import Plane
    >>> from compas_occ.conversions import plane_to_occ_ax3
    >>> plane = Plane([0, 0, 0], [0, 0, 1])
    >>> plane_to_occ_ax3(plane)
    <class 'gp_Ax3'>

    """
    return gp_Ax3(
        point_to_occ(plane.point),
        direction_to_occ(plane.normal),
    )


def frame_to_occ_ax2(frame: Frame) -> gp_Ax2:
    """Convert a COMPAS frame to a right-handed OCC coordinate system.

    Parameters
    ----------
    frame : :class:`compas.geometry.Frame`
        The COMPAS frame.

    Returns
    -------
    ``gp_Ax2``

    See Also
    --------
    :func:`frame_to_occ_ax3`

    Examples
    --------
    >>> from compas.geometry import Frame
    >>> from compas_occ.conversions import frame_to_occ_ax2
    >>> frame = Frame.worldXY()
    >>> frame_to_occ_ax2(frame)
    <class 'gp_Ax2'>

    """
    return gp_Ax2(
        point_to_occ(frame.point),
        direction_to_occ(frame.zaxis),
        direction_to_occ(frame.xaxis),
    )


def frame_to_occ_ax3(frame: Frame) -> gp_Ax3:
    """Convert a COMPAS frame to a right-handed OCC coordinate system.

    Parameters
    ----------
    frame : :class:`compas.geometry.Frame`
        The COMPAS frame.

    Returns
    -------
    ``gp_Ax3``

    See Also
    --------
    :func:`frame_to_occ_ax2`

    Examples
    --------
    >>> from compas.geometry import Frame
    >>> from compas_occ.conversions import frame_to_occ_ax3
    >>> frame = Frame.worldXY()
    >>> frame_to_occ_ax3(frame)
    <class 'gp_Ax3'>

    """
    return gp_Ax3(
        point_to_occ(frame.point),
        direction_to_occ(frame.zaxis),
        direction_to_occ(frame.xaxis),
    )


def circle_to_occ(circle: Circle) -> gp_Circ:
    """Construct an OCC circle from a COMPAS circle.

    Parameters
    ----------
    circle : :class:`compas.geometry.Cicrle`
        The COMPAS circle.

    Returns
    -------
    ``gp_Circ``

    See Also
    --------
    :func:`ellipse_to_occ`

    Examples
    --------
    >>> from compas.geometry import Circle
    >>> from compas_occ.conversions import circle_to_occ
    >>> circle = Circle(1)
    >>> circle_to_occ(circle)
    <class 'gp_Circ'>

    """
    return gp_Circ(
        frame_to_occ_ax2(circle.frame),
        circle.radius,
    )


def ellipse_to_occ(ellipse: Ellipse) -> gp_Elips:
    """Construct an OCC ellipse from a COMPAS ellipse.

    Parameters
    ----------
    ellipse : :class:`compas.geometry.Ellipse`
        The COMPAS ellipse.

    Returns
    -------
    ``gp_Elips``

    See Also
    --------
    :func:`circle_to_occ`

    Examples
    --------
    >>> from compas.geometry import Ellipse
    >>> from compas_occ.conversions import ellipse_to_occ
    >>> ellipse = Ellipse(1, 0.5)
    >>> ellipse_to_occ(ellipse)
    <class 'gp_Elips'>

    """
    return gp_Elips(
        frame_to_occ_ax2(ellipse.frame),
        ellipse.major,
        ellipse.minor,
    )


def sphere_to_occ(sphere: Sphere) -> gp_Sphere:
    """Convert a COMPAS sphere to an OCC sphere.

    Parameters
    ----------
    sphere : :class:`compas.geometry.Sphere`
        The COMPAS sphere.

    Returns
    -------
    ``gp_Sphere``

    See Also
    --------
    :func:`cylinder_to_occ`
    :func:`cone_to_occ`
    :func:`torus_to_occ`

    Examples
    --------
    >>> from compas.geometry import Sphere
    >>> from compas_occ.conversions import sphere_to_occ
    >>> sphere = Sphere(1)
    >>> sphere_to_occ(sphere)
    <class 'gp_Sphere'>

    """
    return gp_Sphere(
        frame_to_occ_ax3(sphere.frame),
        sphere.radius,
    )


def cylinder_to_occ(cylinder: Cylinder) -> gp_Cylinder:
    """Convert a COMPAS cylinder to an OCC cylinder.

    Parameters
    ----------
    cylinder : :class:`compas.geometry.Cylinder`
        The COMPAS cylinder.

    Returns
    -------
    ``gp_Cylinder``

    See Also
    --------
    :func:`sphere_to_occ`
    :func:`cone_to_occ`
    :func:`torus_to_occ`

    Examples
    --------
    >>> from compas.geometry import Cylinder
    >>> from compas_occ.conversions import cylinder_to_occ
    >>> cylinder = Cylinder(1, 1)
    >>> cylinder_to_occ(cylinder)
    <class 'gp_Cylinder'>

    """
    return gp_Cylinder(
        frame_to_occ_ax3(cylinder.frame),
        cylinder.radius,
    )


def cone_to_occ(cone: Cone) -> gp_Cone:
    """Convert a COMPAS cone to an OCC cone.

    Parameters
    ----------
    cone : :class:`compas.geometry.Cone`
        The COMPAS cone.

    Returns
    -------
    ``gp_Cone``

    See Also
    --------
    :func:`sphere_to_occ`
    :func:`cylinder_to_occ`
    :func:`torus_to_occ`

    Examples
    --------
    >>> from compas.geometry import Cone
    >>> from compas_occ.conversions import cone_to_occ
    >>> cone = Cone(1, 1)
    >>> cone_to_occ(cone)
    <class 'gp_Cone'>

    """
    return gp_Cone(
        frame_to_occ_ax3(cone.frame),
        cone.radius,
        cone.height,
    )


def torus_to_occ(torus: Torus) -> gp_Torus:
    """Convert a COMPAS torus to an OCC torus.

    Parameters
    ----------
    torus : :class:`compas.geometry.Torus`
        The COMPAS torus.

    Returns
    -------
    ``gp_Torus``

    See Also
    --------
    :func:`sphere_to_occ`
    :func:`cylinder_to_occ`
    :func:`cone_to_occ`

    Examples
    --------
    >>> from compas.geometry import Torus
    >>> from compas_occ.conversions import torus_to_occ
    >>> torus = Torus(1, 0.5)
    >>> torus_to_occ(torus)
    <class 'gp_Torus'>

    """
    return gp_Torus(
        frame_to_occ_ax3(torus.frame),
        torus.radius_axis,
        torus.radius_pipe,
    )


# =============================================================================
# To COMPAS
# =============================================================================


def point_to_compas(
    point: gp_Pnt,
    cls: Optional[Type[Point]] = None,
) -> Point:
    """Construct a COMPAS point from an OCC point.

    Parameters
    ----------
    point : ``gp_Pnt``
        The OCC point.
    cls : Type[:class:`~compas.geometry.Point`], optional
        The type of COMPAS point.

    Returns
    -------
    :class:`~compas.geometry.Point`

    See Also
    --------
    :func:`point2d_to_compas`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt
    >>> from compas_occ.conversions import point_to_compas
    >>> point = gp_Pnt(0, 0, 0)
    >>> point_to_compas(point)
    Point(x=0.0, y=0.0, z=0.0)

    """
    cls = cls or Point
    return cls(point.X(), point.Y(), point.Z())


def point2d_to_compas(
    point: gp_Pnt2d,
    cls: Optional[Type[Point]] = None,
) -> Point:
    """Construct a COMPAS point from an OCC 2D point.

    Parameters
    ----------
    point : ``gp_Pnt2d``
        The OCC point.
    cls : Type[:class:`~compas.geometry.Point`], optional
        The type of COMPAS point.

    Returns
    -------
    :class:`~compas.geometry.Point`

    See Also
    --------
    :func:`point_to_compas`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt2d
    >>> from compas_occ.conversions import point2d_to_compas
    >>> point = gp_Pnt2d(0, 0)
    >>> point2d_to_compas(point)
    Point(x=0.0, y=0.0, z=0.0)

    """
    cls = cls or Point
    return cls(point.X(), point.Y(), 0)


def vector_to_compas(
    vector: gp_Vec,
    cls: Optional[Type[Vector]] = None,
) -> Vector:
    """Construct a COMPAS vector from an OCC vector.

    Parameters
    ----------
    vector : ``gp_Vec``
        The OCC vector.
    cls : Type[:class:`~compas.geometry.Vector`], optional
        The type of COMPAS vector.

    Returns
    -------
    :class:`~compas.geometry.Vector`

    See Also
    --------
    :func:`vector2d_to_compas`
    :func:`direction_to_compas`
    :func:`axis_to_compas_vector`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Vec
    >>> from compas_occ.conversions import vector_to_compas
    >>> vector = gp_Vec(1, 0, 0)
    >>> vector_to_compas(vector)
    Vector(x=1.0, y=0.0, z=0.0)

    """
    cls = cls or Vector
    return cls(vector.X(), vector.Y(), vector.Z())


def vector2d_to_compas(
    vector: gp_Vec2d,
    cls: Optional[Type[Vector]] = None,
) -> Vector:
    """Construct a COMPAS vector from an OCC 2D vector.

    Parameters
    ----------
    vector : ``gp_Vec2d``
        The OCC vector.
    cls : Type[:class:`~compas.geometry.Vector`], optional
        The type of COMPAS vector.

    Returns
    -------
    :class:`~compas.geometry.Vector`

    See Also
    --------
    :func:`vector_to_compas`
    :func:`direction_to_compas`
    :func:`axis_to_compas_vector`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Vec2d
    >>> from compas_occ.conversions import vector2d_to_compas
    >>> vector = gp_Vec2d(1, 0)
    >>> vector2d_to_compas(vector)
    Vector(x=1.0, y=0.0, z=0.0)

    """
    cls = cls or Vector
    return cls(vector.X(), vector.Y(), 0)


def direction_to_compas(
    vector: gp_Dir,
    cls: Optional[Type[Vector]] = None,
) -> Vector:
    """Construct a COMPAS vector from an OCC direction.

    Parameters
    ----------
    vector : ``gp_Dir``
        The OCC direction.
    cls : Type[:class:`~compas.geometry.Vector`], optional
        The type of COMPAS vector.

    Returns
    -------
    :class:`~compas.geometry.Vector`

    See Also
    --------
    :func:`vector_to_compas`
    :func:`vector2d_to_compas`
    :func:`axis_to_compas_vector`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Dir
    >>> from compas_occ.conversions import direction_to_compas
    >>> vector = gp_Dir(1, 0, 0)
    >>> direction_to_compas(vector)
    Vector(x=1.0, y=0.0, z=0.0)

    """
    cls = cls or Vector
    return cls(vector.X(), vector.Y(), vector.Z())


def axis_to_compas_vector(
    axis: gp_Ax1,
    cls: Optional[Type[Vector]] = None,
) -> Vector:
    """Convert an OCC axis to a COMPAS vector.

    Parameters
    ----------
    axis : ``gp_Ax1``
        The OCC axis.
    cls : Type[:class:`compas.geometry.Vector`], optional
        The type of COMPAS vector.

    Returns
    -------
    :class:`~compas.geometry.Vector`

    See Also
    --------
    :func:`direction_to_compas`
    :func:`vector_to_compas`
    :func:`vector2d_to_compas`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax1
    >>> from compas_occ.conversions import axis_to_compas_vector
    >>> axis = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    >>> axis_to_compas_vector(axis)
    Vector(x=1.0, y=0.0, z=0.0)

    """
    return direction_to_compas(axis.Direction(), cls=cls)


def axis_to_compas(axis: gp_Ax1) -> Tuple[Point, Vector]:
    """Convert an OCC axis to a tuple of COMPAS point and vector.

    Parameters
    ----------
    axis : ``gp_Ax1``
        The OCC axis.

    Returns
    -------
    tuple[:class:`~compas.geometry.Point`, :class:`~compas.geometry.Vector`]

    See Also
    --------
    :func:`axis_to_compas_vector`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax1
    >>> from compas_occ.conversions import axis_to_compas
    >>> axis = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    >>> axis_to_compas(axis)
    (Point(x=0.0, y=0.0, z=0.0), Vector(x=1.0, y=0.0, z=0.0))

    """
    point = point_to_compas(axis.Location())
    vector = direction_to_compas(axis.Direction())
    return point, vector


def line_to_compas(
    lin: gp_Lin,
    cls: Optional[Type[Line]] = None,
) -> Line:
    """Convert an OCC line to a COMPAS line.

    Parameters
    ----------
    lin : ``gp_Lin``
        The OCC line.
    cls : Type[:class:`~compas.geometry.Line`], optional
        The type of COMPAS line.

    Returns
    -------
    :class:`~compas.geometry.Line`

    See Also
    --------
    :func:`line_to_occ`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Lin
    >>> from compas_occ.conversions import line_to_compas
    >>> line = gp_Lin(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    >>> line_to_compas(line)
    Line(Point(x=0.0, y=0.0, z=0.0), Point(x=1.0, y=0.0, z=0.0))

    """
    cls = cls or Line
    point = point_to_compas(lin.Location())
    vector = direction_to_compas(lin.Direction())
    return cls(point, point + vector)


def plane_to_compas(
    pln: gp_Pln,
    cls: Optional[Type[Plane]] = None,
) -> Plane:
    """Convert an OCC plane to a COMPAS plane.

    Parameters
    ----------
    pln : ``gp_Pln``
        The OCC plane.
    cls : Type[:class:`~compas.geometry.Plane`], optional
        The type of COMPAS plane.

    Returns
    -------
    :class:`~compas.geometry.Plane`

    See Also
    --------
    :func:`plane_to_occ`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pln
    >>> from compas_occ.conversions import plane_to_compas
    >>> plane = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    >>> plane_to_compas(plane)
    Plane(point=Point(x=0.0, y=0.0, z=0.0), normal=Vector(x=0.0, y=0.0, z=1.0))

    """
    cls = cls or Plane
    return cls(
        point_to_compas(pln.Location()),
        axis_to_compas_vector(pln.Axis()),
    )


def ax2_to_compas(
    position: gp_Ax2,
    cls: Optional[Type[Frame]] = None,
) -> Frame:
    """Construct a COMPAS frame from an OCC position.

    Parameters
    ----------
    position : ``gp_Ax2``
        The OCC position.
    cls : Type[:class:`~compas.geometry.Frame`], optional
        The type of COMPAS frame.

    Returns
    -------
    :class:`~compas.geometry.Frame`

    See Also
    --------
    :func:`ax3_to_compas`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2
    >>> from compas_occ.conversions import ax2_to_compas
    >>> ax2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> ax2_to_compas(ax2)
    Frame(point=Point(x=0.0, y=0.0, z=0.0), xaxis=Vector(x=1.0, y=0.0, z=0.0), yaxis=Vector(x=0.0, y=1.0, z=0.0))

    """
    cls = cls or Frame
    return cls(
        point_to_compas(position.Location()),
        direction_to_compas(position.XDirection()),
        direction_to_compas(position.YDirection()),
    )


def ax3_to_compas(
    position: gp_Ax3,
    cls: Optional[Type[Frame]] = None,
) -> Frame:
    """Construct a COMPAS frame from an OCC position.

    Parameters
    ----------
    position : ``gp_Ax3``
        The OCC position.
    cls : Type[:class:`~compas.geometry.Frame`], optional
        The type of COMPAS frame.

    Returns
    -------
    :class:`~compas.geometry.Frame`

    See Also
    --------
    :func:`ax2_to_compas`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax3
    >>> from compas_occ.conversions import ax3_to_compas
    >>> ax3 = gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> ax3_to_compas(ax3)
    Frame(point=Point(x=0.0, y=0.0, z=0.0), xaxis=Vector(x=1.0, y=0.0, z=0.0), yaxis=Vector(x=0.0, y=1.0, z=0.0))

    """
    cls = cls or Frame
    return cls(
        point_to_compas(position.Location()),
        direction_to_compas(position.XDirection()),
        direction_to_compas(position.YDirection()),
    )


def location_to_compas(location: TopLoc_Location) -> Frame:
    """Construct a COMPAS frame from an OCC location.

    Parameters
    ----------
    location : ``TopLoc_Location``
        The OCC location.

    Returns
    -------
    :class:`~compas.geometry.Frame`

    Examples
    --------
    >>> from OCC.Core.TopLoc import TopLoc_Location
    >>> from compas_occ.conversions import location_to_compas
    >>> location = TopLoc_Location()
    >>> location_to_compas(location)
    Frame(point=Point(x=0.0, y=0.0, z=0.0), xaxis=Vector(x=1.0, y=0.0, z=0.0), yaxis=Vector(x=0.0, y=1.0, z=0.0))

    """
    t = location.Transformation()

    # transformation.Value is a 1-based 3x4 matrix
    rows, columns = 3, 4
    matrix = [[t.Value(i, j) for j in range(1, columns + 1)] for i in range(1, rows + 1)]
    matrix.append([0.0, 0.0, 0.0, 1.0])  # COMPAS wants a 4x4 matrix
    return Frame.from_transformation(Transformation(matrix))


def circle_to_compas(
    circ: gp_Circ,
    cls: Optional[Type[Circle]] = None,
) -> Circle:
    """Construct a COMPAS circle from an OCC circle.

    Parameters
    ----------
    circ : ``gp_Circ``
        The OCC circle.
    cls : Type[:class:`~compas.geometry.Circle`], optional
        The type of COMPAS circle.

    Returns
    -------
    :class:`~compas.geometry.Circle`

    See Also
    --------
    :func:`ellipse_to_compas`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Circ
    >>> from compas_occ.conversions import circle_to_compas
    >>> ax2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> circ = gp_Circ(ax2, 1)
    >>> circle_to_compas(circ)  # doctest: +ELLIPSIS
    Circle(radius=1.0, frame=Frame(...)

    """
    cls = cls or Circle
    point = point_to_compas(circ.Location())
    frame = ax2_to_compas(circ.Position())
    frame.point = point
    radius = circ.Radius()
    return cls(radius, frame=frame)


def ellipse_to_compas(
    elips: gp_Elips,
    cls: Optional[Type[Ellipse]] = None,
) -> Ellipse:
    """Construc a COMPAS ellipse from an OCC ellipse.

    Parameters
    ----------
    elips : ``gp_Elips``
        The OCC ellipse.
    cls : Type[:class:`~compas.geometry.Ellipse`], optional
        The type of COMPAS ellipse.

    Returns
    -------
    :class:`~compas.geometry.Ellipse`

    See Also
    --------
    :func:`circle_to_compas`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Elips
    >>> from compas_occ.conversions import ellipse_to_compas
    >>> ax2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> elips = gp_Elips(ax2, 1, 0.5)
    >>> ellipse_to_compas(elips)  # doctest: +ELLIPSIS
    Ellipse(major=1.0, minor=0.5, frame=Frame(...))

    """
    cls = cls or Ellipse
    point = point_to_compas(elips.Location())
    frame = ax2_to_compas(elips.Position())
    frame.point = point
    major = elips.MajorRadius()
    minor = elips.MinorRadius()
    return cls(major, minor, frame=frame)


def hyperbola_to_compas(hypr: gp_Hypr) -> Hyperbola:
    """Construct a COMPAS hyperbola from an OCC hyperbola.

    Parameters
    ----------
    hypr : ``gp_Hypr``
        The OCC hyperbola.

    Returns
    -------
    :class:`~compas.geometry.Hyperbola`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Hypr
    >>> from compas_occ.conversions import hyperbola_to_compas
    >>> ax2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> hypr = gp_Hypr(ax2, 1, 0.5)
    >>> hyperbola_to_compas(hypr)  # doctest: +ELLIPSIS
    Hyperbola(major=1.0, minor=0.5, frame=Frame(...))

    """
    point = point_to_compas(hypr.Location())
    frame = ax2_to_compas(hypr.Position())
    frame.point = point
    major = hypr.MajorRadius()
    minor = hypr.MinorRadius()
    return Hyperbola(major, minor, frame=frame)


def parabola_to_compas(parab: gp_Parab) -> Parabola:
    """Construct a COMPAS parabola from an OCC parabola.

    Parameters
    ----------
    parab : ``gp_Parab``
        The OCC parabola.

    Returns
    -------
    :class:`~compas.geometry.Parabola`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Parab
    >>> from compas_occ.conversions import parabola_to_compas
    >>> ax2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> parab = gp_Parab(ax2, 1)
    >>> parabola_to_compas(parab)  # doctest: +ELLIPSIS
    Parabola(focal=2.0, frame=Frame(...))

    """
    point = point_to_compas(parab.Location())
    frame = ax2_to_compas(parab.Position())
    frame.point = point
    length = parab.Parameter()
    return Parabola(length, frame=frame)


def bezier_to_compas(bezier: Geom_BezierCurve) -> Bezier:
    """Construct a COMPAS Bezier curve from an OCC Bezier curve.

    Parameters
    ----------
    bezier : ``Geom_BezierCurve``
        The OCC Bezier curve.

    Returns
    -------
    :class:`~compas.geometry.Bezier`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Parab
    >>> from compas_occ.conversions import bezier_to_compas
    >>> from OCC.Core.Geom import Geom_BezierCurve
    >>> from OCC.Core.TColgp import TColgp_Array1OfPnt
    >>> from OCC.Core.gp import gp_Pnt
    >>> array = TColgp_Array1OfPnt(1, 4)
    >>> array.SetValue(1, gp_Pnt(0, 0, 0))
    >>> array.SetValue(2, gp_Pnt(1, 0, 0))
    >>> array.SetValue(3, gp_Pnt(1, 1, 0))
    >>> array.SetValue(4, gp_Pnt(0, 1, 0))
    >>> bezier = Geom_BezierCurve(array)
    >>> bezier_to_compas(bezier)  # doctest: +ELLIPSIS
    Bezier(points=[...])

    """
    points = [point_to_compas(bezier.Pole(i)) for i in range(1, bezier.NbPoles() + 1)]
    return Bezier(points)


def bspline_to_compas(bspline: Geom_BSplineCurve) -> NurbsCurve:
    """Construct a COMPAS NURBS curve from an OCC B-spline curve.

    Parameters
    ----------
    bspline : ``Geom_BSplineCurve``
        The OCC B-spline curve.

    Returns
    -------
    :class:`~compas.geometry.NurbsCurve`

    """
    return NurbsCurve.from_native(bspline)


def cylinder_to_compas(
    cylinder: gp_Cylinder,
    cls: Optional[Type[Cylinder]] = None,
) -> Cylinder:
    """Convert an OCC cylinder to a COMPAS cylinder.

    Parameters
    ----------
    cylinder : ``gp_Cylinder``
        The OCC cylinder.
    cls : Type[:class:`~compas.geometry.Cylinder`], optional
        The type of COMPAS cylinder.

    Returns
    -------
    :class:`~compas.geometry.Cylinder`

    See Also
    --------
    :func:`compas_sphere_from_occ_sphere`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax3, gp_Cylinder
    >>> from compas_occ.conversions import cylinder_to_compas
    >>> ax3 = gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> cylinder = gp_Cylinder(ax3, 1)
    >>> cylinder_to_compas(cylinder)  # doctest: +ELLIPSIS
    Cylinder(radius=1.0, height=1.0, frame=Frame(...))

    """
    cls = cls or Cylinder
    radius = cylinder.Radius()
    height = 1.0
    frame = ax3_to_compas(cylinder.Position())
    return cls(radius, height, frame=frame)


def sphere_to_compas(
    sphere: gp_Sphere,
    cls: Optional[Type[Sphere]] = None,
) -> Sphere:
    """Convert an OCC sphere to a COMPAS sphere.

    Parameters
    ----------
    sphere : ``gp_Sphere``
        The OCC sphere.
    cls : Type[:class:`~compas.geometry.Sphere`], optional
        The type of COMPAS sphere.

    Returns
    -------
    :class:`~compas.geometry.Sphere`

    See Also
    --------
    :func:`cylinder_to_compas`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax3, gp_Sphere
    >>> from compas_occ.conversions import sphere_to_compas
    >>> ax3 = gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> sphere = gp_Sphere(ax3, 1)
    >>> sphere_to_compas(sphere)  # doctest: +ELLIPSIS
    Sphere(radius=1.0, frame=Frame(...))

    """
    cls = cls or Sphere
    radius = sphere.Radius()
    frame = ax3_to_compas(sphere.Position())
    return cls(radius, frame=frame)
