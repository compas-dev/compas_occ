********************************************************************************
COMPAS OCC
********************************************************************************

.. rst-class:: lead

COMPAS OCC provides an easy-to-use interface to the Python bindings
of the `3D modelling kernel of Open CasCade <https://www.opencascade.com/open-cascade-technology/>`_.

.. figure:: /_images/compas_occ.png
     :figclass: figure
     :class: figure-img img-fluid

:mod:`compas_occ.geometry` defines :class:`~compas_occ.geometry.Curve`, :class:`~compas_occ.geometry.NurbsCurve`,
:class:`~compas_occ.geometry.Surface` and :class:`~compas_occ.geometry.NurbsSurface`, which are wrappers around
``Geom_Curve`` [1]_, ``Geom_BSplineCurve`` [2]_, ``Geom_Surface`` [3]_ and ``Geom_BSplineSurface`` [4]_ of OCC, repsectively.
The :mod:`compas_occ` wrappers provide an API for working with NURBS curves and surfaces similar to the API of RhinoCommon.

:mod:`compas_occ.brep` is a package for working with Boundary Representation (BRep) objects
with the NURBS curves and surfaces of :mod:`compas_occ.geometry` as underlying geometry.


Table of Contents
=================

.. toctree::
   :maxdepth: 3
   :titlesonly:

   Introduction <self>
   installation
   tutorial
   examples
   api
   license


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`


References
==========

.. [1] https://dev.opencascade.org/doc/refman/html/class_geom___curve.html

.. [2] https://dev.opencascade.org/doc/refman/html/class_geom___b_spline_curve.html

.. [3] https://dev.opencascade.org/doc/refman/html/class_geom___surface.html

.. [4] https://dev.opencascade.org/doc/refman/html/class_geom___b_spline_surface.html
