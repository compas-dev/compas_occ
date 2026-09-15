********************************************************************************
Curve From Control Points
********************************************************************************

.. figure:: /_images/example_curve_from_poles.png
    :figclass: figure
    :class: figure-img img-fluid

.. literalinclude:: curve_from_points.py
    :language: python

.. .. code-block:: python

..     print(curve)

.. .. code-block:: text

..     BSplineCurve
..     ------------
..     Poles: [Point(0.000, 0.000, 0.000), Point(3.000, 6.000, 0.000), Point(6.000, -3.000, 3.000), Point(10.000, 0.000, 0.000)]
..     Knots: [0.0, 1.0]
..     Mults: [4, 4]
..     Degree: 3
..     Order: 4
..     Domain: (0.0, 1.0)
..     Closed: False
..     Periodic: False
..     Rational: False
