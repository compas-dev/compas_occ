from typing import Type
from typing import Tuple

from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import Frame
from compas.geometry import Circle
from compas.geometry import Sphere
from compas.geometry import Cylinder
from compas.geometry import Cone
from compas.geometry import Torus

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
from OCC.Core.gp import gp_Pln
from OCC.Core.gp import gp_Sphere
from OCC.Core.gp import gp_Cylinder
from OCC.Core.gp import gp_Cone
from OCC.Core.gp import gp_Torus


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
    >>> Point.to_occ = compas_point_to_occ_point
    >>> point = Point(0, 0, 0)
    >>> point.to_occ()
    <class 'gp_Pnt'>

    """
    return gp_Pnt(*point)


def compas_point_from_occ_point(point: gp_Pnt, cls: Type[Point] = None) -> Point:
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

    """
    cls = cls or Point
    return cls(point.X(), point.Y(), point.Z())


def compas_point_from_occ_point2d(point: gp_Pnt2d, cls: Type[Point] = None) -> Point:
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

    """
    cls = cls or Point
    return cls(point.X(), point.Y(), 0)


def compas_vector_to_occ_vector(vector: Vector) -> gp_Vec:
    """Convert a COMPAS vector to an OCC vector.

    Parameters
    ----------
    vector : :class:`~compas.geometry.Vector`
        The COMPAS vector to convert.

    Returns
    -------
    ``gp_Vec``

    Examples
    --------
    >>> from compas.geometry import Vector
    >>> Vector.to_occ = compas_vector_to_occ_vector
    >>> vector = Vector(1, 0, 0)
    >>> vector.to_occ()
    <class 'gp_Vec'>

    """
    return gp_Vec(*vector)


def compas_vector_from_occ_vector(vector: gp_Vec, cls: Type[Vector] = None) -> Vector:
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

    """
    cls = cls or Vector
    return cls(vector.X(), vector.Y(), vector.Z())


def compas_vector_from_occ_vector2d(
    vector: gp_Vec2d, cls: Type[Vector] = None
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

    """
    cls = cls or Vector
    return cls(vector.X(), vector.Y(), 0)


def compas_vector_to_occ_direction(vector: Vector) -> gp_Dir:
    """Convert a COMPAS vector to an OCC direction.

    Parameters
    ----------
    vector : :class:`~compas.geometry.Vector`
        The COMPAS vector to convert.

    Returns
    -------
    ``gp_Dir``

    Examples
    --------
    >>> from compas.geometry import Vector
    >>> Vector.to_occ_dir = compas_vector_to_occ_direction
    >>> vector = Vector(1, 0, 0)
    >>> vector.to_occ_dir()
    <class 'gp_Dir'>

    """
    return gp_Dir(*vector)


def compas_vector_from_occ_direction(
    vector: gp_Dir, cls: Type[Vector] = None
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

    """
    cls = cls or Vector
    return cls(vector.X(), vector.Y(), vector.Z())


def compas_vector_from_occ_axis(axis: gp_Ax1, cls: Type[Vector] = None) -> Vector:
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

    """
    return compas_vector_from_occ_direction(axis.Direction(), cls=cls)


def compas_axis_to_occ_axis(axis: Tuple[Point, Vector]) -> gp_Ax1:
    """Convert a COMPAS point and vector to an OCC axis.

    Parameters
    ----------
    axis : tuple[:class:`~compas.geometry.Point`, :class:`~compas.geometry.Vector`]
        The COMPAS point and vector.

    Returns
    -------
    ``gp_Ax1``

    Examples
    --------
    >>> from compas.geometry import Vector
    >>> from compas_occ.conversions import compas_axis_to_occ_axis
    >>> vector = Vector(1, 0, 0)
    >>> axis = compas_axis_to_occ_axis(vector)
    <class 'gp_Ax1'>

    """
    return gp_Ax1(
        compas_point_to_occ_point(axis[0]),
        compas_vector_to_occ_direction(axis[1]),
    )


def compas_axis_from_occ_axis(axis: gp_Ax1) -> Tuple[Point, Vector]:
    """Convert an OCC axis to a tuple of COMPAS point and vector.

    Parameters
    ----------
    axis : ``gp_Ax1``
        The OCC axis.

    Returns
    -------
    tuple[:class:`~compas.geometry.Point`, :class:`~compas.geometry.Vector`]

    """
    point = compas_point_from_occ_point(axis.Location())
    vector = compas_vector_from_occ_direction(axis.Direction())
    return point, vector


def compas_line_to_occ_line(line: Line) -> gp_Lin:
    """Convert a COMPAS line to an OCC line.

    Parameters
    ----------
    line : :class:`~compas.geometry.Line`
        The COMPAS line to convert.

    Returns
    -------
    ``gp_Lin``

    Examples
    --------
    >>> from compas.geometry import Line
    >>> Line.to_occ = compas_line_to_occ_line
    >>> line = Line([0, 0, 0], [1, 0, 0])
    >>> line.to_occ()
    <class 'gp_Lin'>

    """
    return gp_Lin(
        compas_point_to_occ_point(line.start),
        compas_vector_to_occ_direction(line.direction),
    )


def compas_line_from_occ_line(lin: gp_Lin, cls: Type[Line] = None) -> Line:
    """Convert an OCC line to a COMPAS line."""
    cls = cls or Line
    point = compas_point_from_occ_point(lin.Location())
    vector = compas_vector_from_occ_direction(lin.Direction())
    return cls(point, point + vector)


def compas_plane_to_occ_plane(plane: Plane) -> gp_Pln:
    """Convert a COMPAS plane to an OCC plane.

    Parameters
    ----------
    plane : :class:`compas.geometry.Plane`
        The COMPAS plane.

    Returns
    -------
    ``gp_Pln``

    """
    return gp_Pln(
        compas_point_to_occ_point(plane.point),
        compas_vector_to_occ_direction(plane.normal),
    )


def compas_plane_from_occ_plane(pln: gp_Pln, cls: Type[Plane] = None) -> Plane:
    """Convert an OCC plane to a COMPAS plane."""
    cls = cls or Plane
    return cls(
        compas_point_from_occ_point(pln.Location()),
        compas_vector_from_occ_axis(pln.Axis()),
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

    """
    return gp_Ax3(
        compas_point_to_occ_point(plane.point),
        compas_vector_to_occ_direction(plane.normal),
    )


def compas_frame_from_occ_ax3(position: gp_Ax3, cls: Type[Frame] = None) -> Frame:
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

    """
    cls = cls or Frame
    return cls(
        compas_point_from_occ_point(position.Location()),
        compas_vector_from_occ_direction(position.XDirection()),
        compas_vector_from_occ_direction(position.YDirection()),
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

    """
    return gp_Circ(compas_plane_to_occ_ax2(circle.plane), circle.radius)


def compas_circle_from_occ_circle(circ: gp_Circ, cls: Type[Circle] = None) -> Circle:
    """Construct a COMPAS circle from an OCC circle."""
    cls = cls or Circle
    point, vector = compas_axis_from_occ_axis(circ.Axis())
    return cls(Plane(point, vector), circ.Radius())


def compas_sphere_to_occ_sphere(sphere: Sphere) -> gp_Sphere:
    """Convert a COMPAS sphere to an OCC sphere.

    Parameters
    ----------
    sphere : :class:`compas.geometry.Sphere`
        The COMPAS sphere.

    Returns
    -------
    ``gp_Sphere``

    """
    plane = Plane(sphere.point, [0, 0, 1])
    return gp_Sphere(compas_plane_to_occ_ax3(plane), sphere.radius)


def compas_cylinder_to_occ_cylinder(cylinder: Cylinder) -> gp_Cylinder:
    """Convert a COMPAS cylinder to an OCC cylinder.

    Parameters
    ----------
    cylinder : :class:`compas.geometry.Cylinder`
        The COMPAS cylinder.

    Returns
    -------
    ``gp_Cylinder``

    """
    return gp_Cylinder(compas_plane_to_occ_ax3(cylinder.plane), cylinder.circle.radius)


def compas_cylinder_from_occ_cylinder(
    cylinder: gp_Cylinder, cls: Type[Cylinder] = None
) -> Cylinder:
    """Convert an OCC cylinder to a COMPAS cylinder."""
    circle = Circle(
        Plane(*compas_axis_from_occ_axis(cylinder.Axis())), cylinder.Radius()
    )
    cls = cls or Cylinder
    return cls(circle, 1.0)


def compas_cone_to_occ_cone(cone: Cone) -> gp_Cone:
    """Convert a COMPAS cone to an OCC cone.

    Parameters
    ----------
    cone : :class:`compas.geometry.Cone`
        The COMPAS cone.

    Returns
    -------
    ``gp_Cone``

    """
    return gp_Cone(compas_plane_to_occ_ax3(cone.plane), cone.circle.radius)


def compas_torus_to_occ_torus(torus: Torus) -> gp_Torus:
    """Convert a COMPAS torus to an OCC torus.

    Parameters
    ----------
    torus : :class:`compas.geometry.Torus`
        The COMPAS torus.

    Returns
    -------
    ``gp_Torus``

    """
    return gp_Torus(
        compas_plane_to_occ_ax3(torus.plane), torus.radius_axis, torus.radius_pipe
    )
