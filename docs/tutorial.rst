********
Tutorial
********

This tutorial gives a brief overview of the functionality of :mod:`compas_occ` and recommended best practices.


Using the plugin system
=======================

:mod:`compas_occ` provides a NURBS and Brep (Boundary Representation) backend for COMPAS based on OpenCasCade.
Although it ca be used as a standalone package, the recommended way to use it is through the plugin system.
The following snippets accomplish the same thing, but the first uses :mod:`compas_occ` directly, and the second uses it as a plugin.

.. code-block:: python

    from compas.geometry import Point
    from compas_occ.geometry import OCCNurbsCurve

    points = [
        Point(0, 0, 0),
        Point(3, 6, 0),
        Point(6, -3, 3),
        Point(10, 0, 0)
    ]

    curve = OCCNurbsCurve.from_points(points)

.. code-block:: python

    from compas.geometry import Point
    from compas.geometry import NurbsCurve

    points = [
        Point(0, 0, 0),
        Point(3, 6, 0),
        Point(6, -3, 3),
        Point(10, 0, 0)
    ]

    curve = NurbsCurve.from_points(points)

The advatage of using the plugin system is that it allows COMPAS to automatically switch to different backends depending on the current environment without chaging the script.
For example, when working in Rhino, the first script will throw an error, whereas the second script will work as expected by switching to RhinoCommon as a backend.


Working with Curves
===================


Working with Surfaces
=====================


Working with Breps
==================


Visualisation
=============

