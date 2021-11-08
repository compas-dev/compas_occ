********************************************************************************
Tutorial
********************************************************************************

``compas_occ`` provides an easy to use interface to the Open Cascade 3D geometry kernel,
built around the Python bindings provided in ``pythonocc-core``.

:mod:`compas_occ.geometry` defines :class:`compas_occ.geometry.OCCNurbsCurve`
and :class:`compas_occ.geometry.OCCNurbsSurface`, which are wrappers around the
``BSplineCurve`` and ``BSplineSurface`` objects of OCC, repsectively.
The :mod:`compas_occ` wrappers provide an API for working with NURBS curves and surfaces
similar to the API of RhinoCommon.

:mod:`compas_occ.brep` is a package for working with Boundary Representation objects
with the NURBS curves and surfaces of :mod:`compas_occ.geometry` as underlying geometry.


Curves
======

.. currentmodule:: compas_occ.geometry

The simplest way to construct a curve is from its control points.

.. code-block:: python

    from compas.geometry import Point
    from compas_occ.geometry import OCCNurbsCurve as NurbsCurve

    points = [Point(0, 0, 0), Point(3, 3, 0), Point(6, -3, 3), Point(9, 0, 0)]
    curve = NurbsCurve.from_points(points)

Other construction methods are

* :meth:`OCCNurbsCurve.from_parameters`
* :meth:`OCCNurbsCurve.from_interpolation`
* :meth:`OCCNurbsCurve.from_step`
* :meth:`OCCNurbsCurve.from_line`
* :meth:`OCCNurbsCurve.from_arc`
* :meth:`OCCNurbsCurve.from_circle`
* :meth:`OCCNurbsCurve.from_ellipse`

Since :class:`OCCNurbsCurve` implements the COMPAS data framework,
there are also the following special methods (see :ref:`Data` for more information).

* :meth:`OCCNurbsCurve.from_data`
* :meth:`OCCNurbsCurve.from_json`

Curves are currently not directly supported by :mod:`compas_view2`.
However, they can be easily visualised by using a high-resolution polyline instead.

.. code-block:: python

    from compas.geometry import Point, Polyline
    from compas_occ.geometry import OCCNurbsCurve as NurbsCurve
    from compas_view2.app import App

    points = [Point(0, 0, 0), Point(3, 3, 0), Point(6, -3, 3), Point(9, 0, 0)]
    curve = NurbsCurve.from_points(points)

    viewer = App()

    viewer.add(Polyline(curve.locus()), linewidth=3)
    viewer.add(Polyline(curve.points), show_points=True)

    viewer.show()


Surfaces
========

*...coming soon...*


Data
====

*...coming soon...*


Rhino
=====

*...coming soon...*


Blender
=======

*...coming soon...*
