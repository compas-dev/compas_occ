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

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, 'curve.stp')

points = []
points.append(Point(-4, 0, 2))
points.append(Point(-7, 2, 2))
points.append(Point(-6, 3, 1))
points.append(Point(-4, 3, -1))
points.append(Point(-3, 5, -2))

spline = BSplineCurve.from_points(points)
spline.to_step(FILE)
```

```python
import os
from compas.geometry import Point
from compas_occ.geometry.curves.bspline import BSplineCurve
from compas_occ.geometry.surfaces.bspline import BSplineSurface

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, 'surface.stp')

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

![Example viz surf1](/docs/_images/example_viz_surf1.png)

```python
from compas.geometry import Point, Polyline

from compas_view2.app import App

from compas_occ.geometry.curves.bspline import BSplineCurve
from compas_occ.geometry.surfaces.bspline import BSplineSurface

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

mesh = surface.to_vizmesh()
boundary = Polyline(mesh.vertices_attributes('xyz', keys=mesh.vertices_on_boundary()))

view = App()
view.add(mesh)
view.add(boundary, linewidth=2)
view.run()
```

![Example viz surf1](/docs/_images/example_intersections1.png)

```python
from compas.geometry import Point, Line, Polyline

from compas_view2.app import App

from compas_occ.geometry.curves.bspline import BSplineCurve
from compas_occ.geometry.surfaces.bspline import BSplineSurface


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
line = Line(Point(0, 4, 0), Point(0, 4, 1))

mesh = surface.to_vizmesh()
boundary = Polyline(mesh.vertices_attributes('xyz', keys=mesh.vertices_on_boundary()))

view = App()
view.add(mesh)
view.add(boundary, linewidth=2)

for point in surface.intersections(line):
    view.add(point, size=10, color=(1, 0, 0))

view.run()
```

![Example viz surf1](/docs/_images/example_heightfield1.png)

```python
from compas.geometry import Point, Polyline

from compas_view2.app import App
from compas_view2.objects import Collection

from compas_occ.geometry.curves.bspline import BSplineCurve
from compas_occ.geometry.surfaces.bspline import BSplineSurface

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

points = Collection(surface.xyz(nu=100, nv=100))

mesh = surface.to_vizmesh()
boundary = Polyline(mesh.vertices_attributes('xyz', keys=mesh.vertices_on_boundary()))

view = App()
view.add(boundary, linewidth=2)
view.add(points, color=(1, 0, 0), size=30)
view.run()
```
