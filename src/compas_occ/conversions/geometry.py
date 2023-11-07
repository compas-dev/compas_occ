from typing import Type
from typing import Tuple
from typing import Optional

from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import Frame
from compas.geometry import Circle
from compas.geometry import Ellipse
from compas.geometry import Sphere
from compas.geometry import Cylinder
from compas.geometry import Cone
from compas.geometry import Torus
from compas.geometry import Transformation

from OCC.Core.gp import gp_Ax1
from OCC.Core.gp import gp_Ax2
from OCC.Core.gp import gp_Ax3
from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Pnt2d
from OCC.Core.gp import gp_Vec
from OCC.Core.gp import gp_Vec2d
from OCC.Core.gp import gp_Dir
from OCC.Core.gp import gp_Lin
from OCC.Core.gp import gp_Circ
from OCC.Core.gp import gp_Elips
from OCC.Core.gp import gp_Pln
from OCC.Core.gp import gp_Sphere
from OCC.Core.gp import gp_Cylinder
from OCC.Core.gp import gp_Cone
from OCC.Core.gp import gp_Torus
from OCC.Core.TopLoc import TopLoc_Location


# =============================================================================
# To OCC
# =============================================================================


def compas_point_to_occ_point(point: Point) -> gp_Pnt:
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
    >>> from compas_occ.conversions import compas_point_to_occ_point
    >>> point = Point(0, 0, 0)
    >>> compas_point_to_occ_point(point)
    <class 'gp_Pnt'>

    """
    return gp_Pnt(*point)


def compas_vector_to_occ_vector(vector: Vector) -> gp_Vec:
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
    :func:`compas_vector_to_occ_direction`

    Examples
    --------
    >>> from compas.geometry import Vector
    >>> from compas_occ.conversions import compas_vector_to_occ_vector
    >>> vector = Vector(1, 0, 0)
    >>> compas_vector_to_occ_vector(vector)
    <class 'gp_Vec'>

    """
    return gp_Vec(*vector)


def compas_vector_to_occ_direction(vector: Vector) -> gp_Dir:
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
    :func:`compas_vector_to_occ_vector`

    Examples
    --------
    >>> from compas.geometry import Vector
    >>> from compas_occ.conversions import compas_vector_to_occ_direction
    >>> vector = Vector(1, 0, 0)
    >>> compas_vector_to_occ_direction(vector)
    <class 'gp_Dir'>

    """
    return gp_Dir(*vector)


def compas_axis_to_occ_axis(axis: Tuple[Point, Vector]) -> gp_Ax1:
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
    :func:`compas_line_to_occ_line`

    Examples
    --------
    >>> from compas.geometry import Point, Vector
    >>> from compas_occ.conversions import compas_axis_to_occ_axis
    >>> point = Point(0, 0, 0)
    >>> vector = Vector(1, 0, 0)
    >>> compas_axis_to_occ_axis((point, vector))
    <class 'gp_Ax1'>

    """
    return gp_Ax1(
        compas_point_to_occ_point(axis[0]),
        compas_vector_to_occ_direction(axis[1]),
    )


def compas_line_to_occ_line(line: Line) -> gp_Lin:
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
    :func:`compas_axis_to_occ_axis`

    Examples
    --------
    >>> from compas.geometry import Line
    >>> from compas_occ.conversions import compas_line_to_occ_line
    >>> line = Line([0, 0, 0], [1, 0, 0])
    >>> compas_line_to_occ_line(line)
    <class 'gp_Lin'>

    """
    return gp_Lin(
        compas_point_to_occ_point(line.start),
        compas_vector_to_occ_direction(line.direction),
    )


def compas_plane_to_occ_plane(plane: Plane) -> gp_Pln:
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
    :func:`compas_plane_to_occ_ax2`
    :func:`compas_plane_to_occ_ax3`

    Examples
    --------
    >>> from compas.geometry import Plane
    >>> from compas_occ.conversions import compas_plane_to_occ_plane
    >>> plane = Plane([0, 0, 0], [0, 0, 1])
    >>> compas_plane_to_occ_plane(plane)
    <class 'gp_Pln'>

    """
    return gp_Pln(
        compas_point_to_occ_point(plane.point),
        compas_vector_to_occ_direction(plane.normal),
    )


def compas_plane_to_occ_ax2(plane: Plane) -> gp_Ax2:
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
    :func:`compas_plane_to_occ_plane`
    :func:`compas_plane_to_occ_ax3`

    Examples
    --------
    >>> from compas.geometry import Plane
    >>> from compas_occ.conversions import compas_plane_to_occ_ax2
    >>> plane = Plane([0, 0, 0], [0, 0, 1])
    >>> compas_plane_to_occ_ax2(plane)
    <class 'gp_Ax2'>

    """
    return gp_Ax2(
        compas_point_to_occ_point(plane.point),
        compas_vector_to_occ_direction(plane.normal),
    )


def compas_plane_to_occ_ax3(plane: Plane) -> gp_Ax3:
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
    :func:`compas_plane_to_occ_plane`
    :func:`compas_plane_to_occ_ax2`

    Examples
    --------
    >>> from compas.geometry import Plane
    >>> from compas_occ.conversions import compas_plane_to_occ_ax3
    >>> plane = Plane([0, 0, 0], [0, 0, 1])
    >>> compas_plane_to_occ_ax3(plane)
    <class 'gp_Ax3'>

    """
    return gp_Ax3(
        compas_point_to_occ_point(plane.point),
        compas_vector_to_occ_direction(plane.normal),
    )


def compas_frame_to_occ_ax2(frame: Frame) -> gp_Ax2:
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
    :func:`compas_frame_to_occ_ax3`

    Examples
    --------
    >>> from compas.geometry import Frame
    >>> from compas_occ.conversions import compas_frame_to_occ_ax2
    >>> frame = Frame.worldXY()
    >>> compas_frame_to_occ_ax2(frame)
    <class 'gp_Ax2'>

    """
    return gp_Ax2(
        compas_point_to_occ_point(frame.point),
        compas_vector_to_occ_direction(frame.zaxis),
        compas_vector_to_occ_direction(frame.xaxis),
    )


def compas_frame_to_occ_ax3(frame: Frame) -> gp_Ax3:
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
    :func:`compas_frame_to_occ_ax2`

    Examples
    --------
    >>> from compas.geometry import Frame
    >>> from compas_occ.conversions import compas_frame_to_occ_ax3
    >>> frame = Frame.worldXY()
    >>> compas_frame_to_occ_ax3(frame)
    <class 'gp_Ax3'>

    """
    return gp_Ax3(
        compas_point_to_occ_point(frame.point),
        compas_vector_to_occ_direction(frame.zaxis),
        compas_vector_to_occ_direction(frame.xaxis),
    )


def compas_circle_to_occ_circle(circle: Circle) -> gp_Circ:
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
    :func:`compas_ellipse_to_occ_ellipse`

    Examples
    --------
    >>> from compas.geometry import Circle
    >>> from compas_occ.conversions import compas_circle_to_occ_circle
    >>> circle = Circle(1)
    >>> compas_circle_to_occ_circle(circle)
    <class 'gp_Circ'>

    """
    return gp_Circ(
        compas_frame_to_occ_ax2(circle.frame),
        circle.radius,
    )


def compas_ellipse_to_occ_ellipse(ellipse: Ellipse) -> gp_Elips:
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
    :func:`compas_circle_to_occ_circle`

    Examples
    --------
    >>> from compas.geometry import Ellipse
    >>> from compas_occ.conversions import compas_ellipse_to_occ_ellipse
    >>> ellipse = Ellipse(1, 0.5)
    >>> compas_ellipse_to_occ_ellipse(ellipse)
    <class 'gp_Elips'>

    """
    return gp_Elips(
        compas_frame_to_occ_ax2(ellipse.frame),
        ellipse.major,
        ellipse.minor,
    )


def compas_sphere_to_occ_sphere(sphere: Sphere) -> gp_Sphere:
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
    :func:`compas_cylinder_to_occ_cylinder`
    :func:`compas_cone_to_occ_cone`
    :func:`compas_torus_to_occ_torus`

    Examples
    --------
    >>> from compas.geometry import Sphere
    >>> from compas_occ.conversions import compas_sphere_to_occ_sphere
    >>> sphere = Sphere(1)
    >>> compas_sphere_to_occ_sphere(sphere)
    <class 'gp_Sphere'>

    """
    return gp_Sphere(
        compas_frame_to_occ_ax3(sphere.frame),
        sphere.radius,
    )


def compas_cylinder_to_occ_cylinder(cylinder: Cylinder) -> gp_Cylinder:
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
    :func:`compas_sphere_to_occ_sphere`
    :func:`compas_cone_to_occ_cone`
    :func:`compas_torus_to_occ_torus`

    Examples
    --------
    >>> from compas.geometry import Cylinder
    >>> from compas_occ.conversions import compas_cylinder_to_occ_cylinder
    >>> cylinder = Cylinder(1, 1)
    >>> compas_cylinder_to_occ_cylinder(cylinder)
    <class 'gp_Cylinder'>

    """
    return gp_Cylinder(
        compas_frame_to_occ_ax3(cylinder.frame),
        cylinder.radius,
    )


def compas_cone_to_occ_cone(cone: Cone) -> gp_Cone:
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
    :func:`compas_sphere_to_occ_sphere`
    :func:`compas_cylinder_to_occ_cylinder`
    :func:`compas_torus_to_occ_torus`

    Examples
    --------
    >>> from compas.geometry import Cone
    >>> from compas_occ.conversions import compas_cone_to_occ_cone
    >>> cone = Cone(1, 1)
    >>> compas_cone_to_occ_cone(cone)
    <class 'gp_Cone'>

    """
    return gp_Cone(
        compas_frame_to_occ_ax3(cone.frame),
        cone.radius,
        cone.height,
    )


def compas_torus_to_occ_torus(torus: Torus) -> gp_Torus:
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
    :func:`compas_sphere_to_occ_sphere`
    :func:`compas_cylinder_to_occ_cylinder`
    :func:`compas_cone_to_occ_cone`

    Examples
    --------
    >>> from compas.geometry import Torus
    >>> from compas_occ.conversions import compas_torus_to_occ_torus
    >>> torus = Torus(1, 0.5)
    >>> compas_torus_to_occ_torus(torus)
    <class 'gp_Torus'>

    """
    return gp_Torus(
        compas_frame_to_occ_ax3(torus.frame),
        torus.radius_axis,
        torus.radius_pipe,
    )


# =============================================================================
# To COMPAS
# =============================================================================


def compas_point_from_occ_point(
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
    :func:`compas_point_from_occ_point2d`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt
    >>> from compas_occ.conversions import compas_point_from_occ_point
    >>> point = gp_Pnt(0, 0, 0)
    >>> compas_point_from_occ_point(point)
    Point(0.0, 0.0, z=0.0)

    """
    cls = cls or Point
    return cls(point.X(), point.Y(), point.Z())


def compas_point_from_occ_point2d(
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
    :func:`compas_point_from_occ_point`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt2d
    >>> from compas_occ.conversions import compas_point_from_occ_point2d
    >>> point = gp_Pnt2d(0, 0)
    >>> compas_point_from_occ_point2d(point)
    Point(0.0, 0.0, z=0.0)

    """
    cls = cls or Point
    return cls(point.X(), point.Y(), 0)


def compas_vector_from_occ_vector(
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
    :func:`compas_vector_from_occ_vector2d`
    :func:`compas_vector_from_occ_direction`
    :func:`compas_vector_from_occ_axis`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Vec
    >>> from compas_occ.conversions import compas_vector_from_occ_vector
    >>> vector = gp_Vec(1, 0, 0)
    >>> compas_vector_from_occ_vector(vector)
    Vector(x=1.0, y=0.0, z=0.0)

    """
    cls = cls or Vector
    return cls(vector.X(), vector.Y(), vector.Z())


def compas_vector_from_occ_vector2d(
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
    :func:`compas_vector_from_occ_vector`
    :func:`compas_vector_from_occ_direction`
    :func:`compas_vector_from_occ_axis`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Vec2d
    >>> from compas_occ.conversions import compas_vector_from_occ_vector2d
    >>> vector = gp_Vec2d(1, 0)
    >>> compas_vector_from_occ_vector2d(vector)
    Vector(x=1.0, y=0.0, z=0.0)

    """
    cls = cls or Vector
    return cls(vector.X(), vector.Y(), 0)


def compas_vector_from_occ_direction(
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
    :func:`compas_vector_from_occ_vector`
    :func:`compas_vector_from_occ_vector2d`
    :func:`compas_vector_from_occ_axis`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Dir
    >>> from compas_occ.conversions import compas_vector_from_occ_direction
    >>> vector = gp_Dir(1, 0, 0)
    >>> compas_vector_from_occ_direction(vector)
    Vector(x=1.0, y=0.0, z=0.0)

    """
    cls = cls or Vector
    return cls(vector.X(), vector.Y(), vector.Z())


def compas_vector_from_occ_axis(
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
    :func:`compas_vector_from_occ_direction`
    :func:`compas_vector_from_occ_vector`
    :func:`compas_vector_from_occ_vector2d`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax1
    >>> from compas_occ.conversions import compas_vector_from_occ_axis
    >>> axis = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    >>> compas_vector_from_occ_axis(axis)
    Vector(x=1.0, y=0.0, z=0.0)

    """
    return compas_vector_from_occ_direction(axis.Direction(), cls=cls)


def compas_axis_from_occ_axis(axis: gp_Ax1) -> Tuple[Point, Vector]:
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
    :func:`compas_vector_from_occ_axis`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax1
    >>> from compas_occ.conversions import compas_axis_from_occ_axis
    >>> axis = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    >>> compas_axis_from_occ_axis(axis)
    (Point(0.0, 0.0, z=0.0), Vector(x=1.0, y=0.0, z=0.0))

    """
    point = compas_point_from_occ_point(axis.Location())
    vector = compas_vector_from_occ_direction(axis.Direction())
    return point, vector


def compas_line_from_occ_line(
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
    :func:`compas_line_to_occ_line`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Lin
    >>> from compas_occ.conversions import compas_line_from_occ_line
    >>> line = gp_Lin(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    >>> compas_line_from_occ_line(line)
    Line(Point(0.0, 0.0, z=0.0), Point(1.0, 0.0, z=0.0))

    """
    cls = cls or Line
    point = compas_point_from_occ_point(lin.Location())
    vector = compas_vector_from_occ_direction(lin.Direction())
    return cls(point, point + vector)


def compas_plane_from_occ_plane(
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
    :func:`compas_plane_to_occ_plane`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pln
    >>> from compas_occ.conversions import compas_plane_from_occ_plane
    >>> plane = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    >>> compas_plane_from_occ_plane(plane)
    Plane(point=Point(0.0, 0.0, z=0.0), normal=Vector(x=0.0, y=0.0, z=1.0))

    """
    cls = cls or Plane
    return cls(
        compas_point_from_occ_point(pln.Location()),
        compas_vector_from_occ_axis(pln.Axis()),
    )


def compas_frame_from_occ_ax2(
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
    :func:`compas_frame_from_occ_ax3`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2
    >>> from compas_occ.conversions import compas_frame_from_occ_ax2
    >>> ax2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> compas_frame_from_occ_ax2(ax2)
    Frame(point=Point(0.0, 0.0, z=0.0), xaxis=Vector(x=1.0, y=0.0, z=0.0), yaxis=Vector(x=0.0, y=1.0, z=0.0))

    """
    cls = cls or Frame
    return cls(
        compas_point_from_occ_point(position.Location()),
        compas_vector_from_occ_direction(position.XDirection()),
        compas_vector_from_occ_direction(position.YDirection()),
    )


def compas_frame_from_occ_ax3(
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
    :func:`compas_frame_from_occ_ax2`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax3
    >>> from compas_occ.conversions import compas_frame_from_occ_ax3
    >>> ax3 = gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> compas_frame_from_occ_ax3(ax3)
    Frame(point=Point(0.0, 0.0, z=0.0), xaxis=Vector(x=1.0, y=0.0, z=0.0), yaxis=Vector(x=0.0, y=1.0, z=0.0))

    """
    cls = cls or Frame
    return cls(
        compas_point_from_occ_point(position.Location()),
        compas_vector_from_occ_direction(position.XDirection()),
        compas_vector_from_occ_direction(position.YDirection()),
    )


def compas_frame_from_occ_location(location: TopLoc_Location) -> Frame:
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
    >>> from compas_occ.conversions import compas_frame_from_occ_location
    >>> location = TopLoc_Location()
    >>> compas_frame_from_occ_location(location)
    Frame(point=Point(0.0, 0.0, z=0.0), xaxis=Vector(x=1.0, y=0.0, z=0.0), yaxis=Vector(x=0.0, y=1.0, z=0.0))

    """
    t = location.Transformation()

    # transformation.Value is a 1-based 3x4 matrix
    rows, columns = 3, 4
    matrix = [
        [t.Value(i, j) for j in range(1, columns + 1)] for i in range(1, rows + 1)
    ]
    matrix.append([0.0, 0.0, 0.0, 1.0])  # COMPAS wants a 4x4 matrix
    return Frame.from_transformation(Transformation(matrix))


def compas_circle_from_occ_circle(
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
    :func:`compas_ellipse_from_occ_ellipse`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Circ
    >>> from compas_occ.conversions import compas_circle_from_occ_circle
    >>> ax2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> circ = gp_Circ(ax2, 1)
    >>> compas_circle_from_occ_circle(circ)
    Circle(radius=1.0, frame=Frame(point=Point(0.0, 0.0, z=0.0), xaxis=Vector(x=1.0, y=0.0, z=-0.0), yaxis=Vector(x=-0.0, y=1.0, z=0.0)))

    """
    cls = cls or Circle
    point = compas_point_from_occ_point(circ.Location())
    frame = compas_frame_from_occ_ax2(circ.Position())
    frame.point = point
    radius = circ.Radius()
    return cls(radius, frame=frame)


def compas_ellipse_from_occ_ellipse(
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
    :func:`compas_circle_from_occ_circle`

    Examples
    --------
    >>> from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Elips
    >>> from compas_occ.conversions import compas_ellipse_from_occ_ellipse
    >>> ax2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> elips = gp_Elips(ax2, 1, 0.5)
    >>> compas_ellipse_from_occ_ellipse(elips)
    Ellipse(major=1.0, minor=0.5, frame=Frame(point=Point(0.0, 0.0, z=0.0), xaxis=Vector(x=1.0, y=0.0, z=0.0), yaxis=Vector(x=0.0, y=1.0, z=0.0)))

    """
    cls = cls or Ellipse
    point = compas_point_from_occ_point(elips.Location())
    frame = compas_frame_from_occ_ax2(elips.Position())
    frame.point = point
    major = elips.MajorRadius()
    minor = elips.MinorRadius()
    return cls(major, minor, frame=frame)


def compas_cylinder_from_occ_cylinder(
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
    >>> from compas_occ.conversions import compas_cylinder_from_occ_cylinder
    >>> ax3 = gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    >>> cylinder = gp_Cylinder(ax3, 1)
    >>> compas_cylinder_from_occ_cylinder(cylinder)
    Cylinder(radius=1.0, height=1.0, frame=Frame(point=Point(0.0, 0.0, z=0.0), xaxis=Vector(x=1.0, y=0.0, z=-0.0), yaxis=Vector(x=-0.0, y=1.0, z=0.0)))

    """
    cls = cls or Cylinder
    radius = cylinder.Radius()
    height = 1.0
    frame = compas_frame_from_occ_ax3(cylinder.Position())
    return cls(radius, height, frame=frame)
