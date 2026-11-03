# Brep with Hole

This example builds a trimmed NURBS face and approximates it with an explicit
[`Deflection`](https://compas.dev/compas/latest/api/generated/compas.geometry.Deflection.html)
strategy. Linear deflection is expressed in model units and angular deflection in
degrees; the OCC provider performs any required conversion to radians. The returned
`Tessellation.polylines` contain discretized BRep edge boundaries, including the
trimmed hole.

OCC triangulates every face independently. Therefore, coincident vertices along
shared edges and periodic seams remain duplicated in the indexed triangle buffers.
The tessellation preserves the geometric boundary, but its indices should not be
assumed to form a welded or topologically watertight mesh. Convert explicitly and
weld separately if a downstream operation requires that topology.

The trims belong to the BRep face, not to its underlying NURBS surface. Extracting
`face.nurbssurface` and tessellating that surface produces the untrimmed parameter
domain; it does not preserve the outer boundary or the hole constructed here.

![Example Brep with Hole](../../assets/images/example_brep_with_hole.png)

```python
---8<--- "docs/examples/breps/brep_with_hole.py"
```
