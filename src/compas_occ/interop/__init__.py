"""
********************************************************************************
compas_occ.interop
********************************************************************************

.. currentmodule:: compas_occ.interop

Arrays
======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    array1_from_floats1
    array1_from_integers1
    array1_from_points1
    array2_from_points2
    points1_from_array1
    points2_from_array2

Primitives
==========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    compas_point_to_occ_point
    compas_point_from_occ_point
    compas_vector_to_occ_vector
    compas_vector_to_occ_direction
    compas_vector_from_occ_vector
    compas_line_to_occ_line

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
from .arrays import array1_from_integers1  # noqa: F401
from .arrays import array1_from_floats1  # noqa: F401
from .arrays import array1_from_points1  # noqa: F401
from .arrays import harray1_from_points1  # noqa: F401
from .arrays import array2_from_points2  # noqa: F401
from .arrays import points1_from_array1  # noqa: F401
from .arrays import points2_from_array2  # noqa: F401

from .primitives import compas_point_to_occ_point  # noqa: F401
from .primitives import compas_point_from_occ_point  # noqa: F401
from .primitives import compas_vector_to_occ_vector  # noqa: F401
from .primitives import compas_vector_to_occ_direction  # noqa: F401
from .primitives import compas_vector_from_occ_vector  # noqa: F401
from .primitives import compas_line_to_occ_line  # noqa: F401

from .meshes import triangle_to_face  # noqa: F401
from .meshes import quad_to_face  # noqa: F401
from .meshes import ngon_to_face  # noqa: F401
from .meshes import compas_mesh_to_occ_shell  # noqa: F401
from .meshes import compas_quadmesh_to_occ_shell  # noqa: F401
from .meshes import compas_trimesh_to_occ_shell  # noqa: F401
