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

### Export BSplineSurface to STP

```python
import os
from compas.geometry import Point
from compas_occ.geometry.curves import BSplineCurve
from compas_occ.geometry.surfaces import BSplineSurface

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

### Viz BSplineSurface with View2

![Example](/docs/_images/example_viz_surf1.png)

```python
from compas.geometry import Point, Polyline

from compas_view2.app import App

from compas_occ.geometry.curves import BSplineCurve
from compas_occ.geometry.surfaces import BSplineSurface

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

### Intersect BSplineSurface with Line

![Example](/docs/_images/example_intersections1.png)

```python
from compas.geometry import Point, Line, Polyline

from compas_view2.app import App

from compas_occ.geometry.curves import BSplineCurve
from compas_occ.geometry.surfaces import BSplineSurface


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

### BSplineSurface points along UV

![Example](/docs/_images/example_heightfield1.png)

```python
from compas.geometry import Point, Polyline

from compas_view2.app import App
from compas_view2.objects import Collection

from compas_occ.geometry.curves import BSplineCurve
from compas_occ.geometry.surfaces import BSplineSurface

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

### BSplineSurface frames along UV

![Example](/docs/_images/example_frames1.png)

```python
from compas.geometry import Point, Polyline
from compas.utilities import i_to_rgb, meshgrid, linspace, flatten

from compas_view2.app import App
from compas_view2.objects import Collection

from compas_occ.geometry.curves import BSplineCurve
from compas_occ.geometry.surfaces import BSplineSurface

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

U, V = meshgrid(surface.uspace(30), surface.vspace(20), 'ij')

frames = [surface.frame_at(u, v) for u, v in zip(flatten(U[1:]), flatten(V))]

mesh = surface.to_vizmesh()
boundary = Polyline(mesh.vertices_attributes('xyz', keys=mesh.vertices_on_boundary()))

view = App()
view.add(mesh)
view.add(boundary, linewidth=2)

for frame in frames:
    view.add(frame, size=0.1)

view.run()
```

### BRep boolean union primitives (export Rhino)

![Example](/docs/_images/example_boolean_union1.png)

```python
import os

from compas.geometry import Frame
from compas_occ.brep.primitives import Box, Sphere
from compas_occ.brep.booleans import boolean_union_shape_shape

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '__fuse.stp')

box = Box(Frame.worldXY(), 1, 1, 1)
sphere = Sphere([0.5 * box.xsize, 0.5 * box.ysize, 0.5 * box.zsize], 0.5)

shape = boolean_union_shape_shape(box, sphere)

shape.to_step(FILE)
```

### BRep boolean union primitives

![Example](/docs/_images/example_boolean_union2.png)

```python
from compas.geometry import Polyline, Frame
from compas_occ.interop.shapes import Box, Sphere
from compas_occ.brep.booleans import boolean_union_shape_shape
from compas_occ.geometry.surfaces import BSplineSurface
from compas_occ.geometry.curves import BSplineCurve

from compas_view2.app import App
from compas_view2.objects import Object, BoxObject, SphereObject

from OCC.Core.BRep import BRep_Tool_Surface, BRep_Tool_Curve
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
from OCC.Extend.TopologyUtils import TopologyExplorer

Object.register(Box, BoxObject)
Object.register(Sphere, SphereObject)

box = Box(Frame.worldXY(), 1, 1, 1)
sphere = Sphere([0.5 * box.xsize, 0.5 * box.ysize, 0.5 * box.zsize], 0.5)
shape = boolean_union_shape_shape(box, sphere)
converter = BRepBuilderAPI_NurbsConvert(shape.occ_shape, True)
shape_exp = TopologyExplorer(converter.Shape())

viewer = App()

for face in shape_exp.faces():
    srf = BRep_Tool_Surface(face)
    surface = BSplineSurface.from_occ(srf)
    viewer.add(surface.to_vizmesh(resolution=16), show_edges=True)

for edge in shape_exp.edges():
    res = BRep_Tool_Curve(edge)
    if len(res) == 3:
        crv, u, v = res
        curve = BSplineCurve.from_occ(crv)
        viewer.add(Polyline(curve.to_locus(resolution=16)), linecolor=(1, 0, 0), linewidth=5)

viewer.run()
```
