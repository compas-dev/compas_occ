"""
********************************************************************************
compas_occ.conversions
********************************************************************************

.. currentmodule:: compas_occ.conversions

Arrays
======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    array1_from_floats1
    array1_from_integers1
    array1_from_points1
    array2_from_floats2
    array2_from_points2
    floats2_from_array2
    harray1_from_points1
    points1_from_array1
    points2_from_array2

Primitives
==========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    compas_axis_from_occ_axis
    compas_axis_to_occ_axis
    compas_circle_from_occ_circle
    compas_circle_to_occ_circle
    compas_cone_to_occ_cone
    compas_cylinder_from_occ_cylinder
    compas_cylinder_to_occ_cylinder
    compas_frame_from_location
    compas_frame_from_occ_ax3
    compas_line_from_occ_line
    compas_line_to_occ_line
    compas_plane_from_occ_plane
    compas_plane_to_occ_ax2
    compas_plane_to_occ_ax3
    compas_plane_to_occ_plane
    compas_point_from_occ_point
    compas_point_from_occ_point2d
    compas_point_to_occ_point
    compas_sphere_to_occ_sphere
    compas_torus_to_occ_torus
    compas_vector_to_occ_direction
    compas_vector_to_occ_vector
    compas_vector_from_occ_axis
    compas_vector_from_occ_vector
    compas_vector_from_occ_vector2d

Transformations
===============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    compas_transformation_to_trsf


Meshes
======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    compas_mesh_to_occ_shell
    compas_quadmesh_to_occ_shell
    compas_trimesh_to_occ_shell
    ngon_to_face
    quad_to_face
    triangle_to_face

"""
from .arrays import array1_from_floats1
from .arrays import array1_from_integers1
from .arrays import array1_from_points1
from .arrays import array2_from_floats2
from .arrays import array2_from_points2
from .arrays import floats2_from_array2
from .arrays import harray1_from_points1
from .arrays import points1_from_array1
from .arrays import points2_from_array2

from .primitives import compas_axis_from_occ_axis
from .primitives import compas_axis_to_occ_axis
from .primitives import compas_circle_from_occ_circle
from .primitives import compas_circle_to_occ_circle
from .primitives import compas_cone_to_occ_cone
from .primitives import compas_cylinder_from_occ_cylinder
from .primitives import compas_cylinder_to_occ_cylinder
from .primitives import compas_frame_from_location
from .primitives import compas_frame_from_occ_ax3
from .primitives import compas_line_from_occ_line
from .primitives import compas_line_to_occ_line
from .primitives import compas_plane_from_occ_plane
from .primitives import compas_plane_to_occ_ax2
from .primitives import compas_plane_to_occ_ax3
from .primitives import compas_plane_to_occ_plane
from .primitives import compas_point_from_occ_point
from .primitives import compas_point_from_occ_point2d
from .primitives import compas_point_to_occ_point
from .primitives import compas_sphere_to_occ_sphere
from .primitives import compas_torus_to_occ_torus
from .primitives import compas_vector_to_occ_direction
from .primitives import compas_vector_to_occ_vector
from .primitives import compas_vector_from_occ_axis
from .primitives import compas_vector_from_occ_vector
from .primitives import compas_vector_from_occ_vector2d

from .transformations import compas_transformation_to_trsf

from .meshes import compas_mesh_to_occ_shell
from .meshes import compas_quadmesh_to_occ_shell
from .meshes import compas_trimesh_to_occ_shell
from .meshes import ngon_to_face
from .meshes import quad_to_face
from .meshes import triangle_to_face

__all__ = [
    "array1_from_floats1",
    "array1_from_integers1",
    "array1_from_points1",
    "array2_from_floats2",
    "array2_from_points2",
    "compas_axis_from_occ_axis",
    "compas_axis_to_occ_axis",
    "compas_circle_from_occ_circle",
    "compas_circle_to_occ_circle",
    "compas_cone_to_occ_cone",
    "compas_cylinder_from_occ_cylinder",
    "compas_cylinder_to_occ_cylinder",
    "compas_frame_from_location",
    "compas_frame_from_occ_ax3",
    "compas_line_from_occ_line",
    "compas_line_to_occ_line",
    "compas_plane_from_occ_plane",
    "compas_plane_to_occ_ax2",
    "compas_plane_to_occ_ax3",
    "compas_plane_to_occ_plane",
    "compas_point_from_occ_point",
    "compas_point_from_occ_point2d",
    "compas_point_to_occ_point",
    "compas_sphere_to_occ_sphere",
    "compas_torus_to_occ_torus",
    "compas_transformation_to_trsf",
    "compas_vector_to_occ_direction",
    "compas_vector_to_occ_vector",
    "compas_vector_from_occ_axis",
    "compas_vector_from_occ_vector",
    "compas_vector_from_occ_vector2d",
    "compas_mesh_to_occ_shell",
    "compas_quadmesh_to_occ_shell",
    "compas_trimesh_to_occ_shell",
    "floats2_from_array2",
    "harray1_from_points1",
    "ngon_to_face",
    "points1_from_array1",
    "points2_from_array2",
    "quad_to_face",
    "triangle_to_face",
]
