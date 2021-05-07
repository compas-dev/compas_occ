# COMPAS OCC

COMPAS wrapper for the Python bindings of OCC

**This package is in early stages of development!**

----

## Installation

```bash
conda create -n occ python=3.8 compas compas_view2 pythonocc-core
conda activate occ
pip install -e .
```

## Scripts

Initial API exploration scripts are available in `scripts`.

```python
import os
from compas.geometry import Point
from compas_occ.geometry.curves.bspline import BSplineCurve
from compas_occ.geometry.surfaces.bspline import BSplineSurface

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '__surface.stp')

points1 = []
points1.append(Point(-4, 0, 2))
points1.append(Point(-7, 2, 2))
points1.append(Point(-6, 3, 1))
points1.append(Point(-4, 3, -1))
points1.append(Point(-3, 5, -2))
spline1 = BSplineCurve.from_points(points1)

points2 = []
points2.append(Point(-4, 0, 2))
points2.append(Point(-2, 2, 0))
points2.append(Point(2, 3, -1))
points2.append(Point(3, 7, -2))
points2.append(Point(4, 9, -1))
spline2 = BSplineCurve.from_points(points2)

surface = BSplineSurface.from_fill(spline1, spline2)
surface.to_step(FILE)
```
