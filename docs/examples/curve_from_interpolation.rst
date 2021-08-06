********************************************************************************
Curve From Interpolation
********************************************************************************

.. figure:: /_images/example_curve_from_interpolation.png
    :figclass: figure
    :class: figure-img img-fluid

.. literalinclude:: curve_from_interpolation.py
    :language: python

.. code-block:: python

    print(curve)

.. code-block:: text

    BSplineCurve
    ------------
    Points: [Point(0.000, 0.000, 0.000), Point(0.194, 0.505, -0.029), Point(0.793, 1.425, 0.037), Point(1.946, 2.197, 0.312), Point(3.109, 2.053, 0.692), Point(4.130, 1.482, 1.013), Point(5.171, 0.737, 1.259), Point(6.257, -0.016, 1.369), Point(7.462, -0.606, 1.266), Point(8.836, -0.676, 0.783), Point(9.652, -0.331, 0.293), Point(10.000, 0.000, 0.000)]
    Weights: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    Knots: [0.0, 1.790890101723612, 2.987313475210379, 4.064961621935241, 5.279860572309372, 6.615531720757587, 7.965972642272798, 9.255497783041292, 10.558981966432055, 12.18974969841392]
    Mults: [4, 1, 1, 1, 1, 1, 1, 1, 1, 4]
    Degree: 3
    Order: 4
    Domain: (0.0, 12.18974969841392)
    Closed: False
    Periodic: False
    Rational: False
