# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] 2024-02-01

### Added

* Added `OCCBrep.trim` and `OCCBrep.trimmed`.
* Added `OCCBrep.slice`.
* Added `OCCBrep.split`.
* Added `OCCBrep.fillet` and `OCCBrep.filleted`.
* Added `OCCCurve.parameter_at_distance`.
* Added `compas_occ.conversions.compas_frame_from_location`.
* Added `OCCBrep.native_brep` as alias for `OCCBrep.occ_shape`.
* Added `is_equal` and `is_same` for `OCCBrepVertex`, `OCCBrepEdge`, `OCCBrepLoop`, `OCCBrepFace`.
* Added correct type info to `OCCBrepVertex.occ_vertex`.
* Added correct type info to `OCCBrepEdge.occ_edge`.
* Added correct type info to `OCCBrepLoop.occ_wire`.
* Added correct type info to `OCCBrepFace.occ_face`.
* Added `OCCBrepLoop.occ_shape`.
* Added `OCCBrep.from_iges`.
* Added `OCCBrep.to_stl`.
* Added `OCCBrep.to_iges`.
* Added `OCCBrepVertex.is_same` and `OCCBrepVertex.is_equal`.
* Added `OCCBrepEdge.is_same` and `OCCBrepEdge.is_equal`.
* Added `OCCBrepLoop.is_same` and `OCCBrepLoop.is_equal`.
* Added `OCCBrepFace.is_same` and `OCCBrepFace.is_equal`.

### Changed

* Changed `OCCBrep` to be a pluggin for `compas.geometry.Brep`.
* Fixed the error when calling `OCCBrep.frame`.
* Fixed `AttributeError` when calling `OCCBrep.loops`.
* Updated `compas-actions.build` workflow to v3.
* Updated github workflow to latest version.

### Removed

## [0.7.1] 2023-03-21

### Added

### Changed

* Fixed bug in generation of tessellation mesh.

### Removed

## [0.7.0] 2022-11-06

### Added

* Added `compas_occ.geometry.OCCSurface.from_plane`.
* Added `compas_occ.geometry.OCCSurface.intersections_with_curve`.
* Added `compas_occ.brep.BRepFace.to_polygon`.
* Added `compas_occ.brep.BRep.edge_faces`.

### Changed

* Changed default units to MM in `compas_occ.brep.BRep`.

### Removed

## [0.6.0] 2022-10-07

### Added

* Added `BRep.from_polygons`.
* Added `BRep.from_extrusion`.
* Added `BRep.from_sweep`.
* Added `BRep.to_viewmesh`.
* Added `BRep.overlap`.
* Added `BRepFace.from_polygon`.

### Changed

* Fixed bug in `BRep.transform`.
* Changed `BRep.vertices`, `BRep.edges`, `BRep.loops`, `BRep.faces`, `BRep.shells`, `BRep.solids` to only be recreated once unerlying shape is changed.
* Changed implementation of `BRep.to_tessellation` to use range loop over individual nodes of triangulation instead of node list accessor.

### Removed

## [0.5.0] 2022-07-22

### Added

* Added `compas_occ.geometry.OCCRevolutionSurface`.
* Added `compas_occ.conversions.compas_axis_to_occ_axis`.
* Added `compas_occ.conversions.compas_axis_from_occ_axis`.
* Added `compas_occ.geometry.OCCExtrusionSurface`.
* Added `compas_occ.geometry.OCCNurbsSurface.from_extrusion`.
* Added `compas_occ.geometry.OCCCurve.divide_by_count`.
* Added `compas_occ.geometry.OCCCurve.divide` as alias for `compas_occ.geometry.OCCCurve.divide_by_count`.
* Added `compas_occ.geometry.OCCCurve.projected`.
* Added `compas_occ.geometry.OCCCurve.embedded`.
* Added `compas_occ.brep.BRep.from_faces`.
* Added `compas_occ.brep.BRep.from_polygons`.
* Added `compas_occ.brep.BRep.check`.
* Added `compas_occ.brep.BRep.sew`.
* Added `compas_occ.brep.BRep.fix`.
* Added `compas_occ.brep.BRep.transform`.
* Added `compas_occ.brep.BRep.transformed`.
* Added `compas_occ.brep.BRep.from_step`.
* Added `compas_occ.brep.BRep.from_shape`.
* Added `compas_occ.brep.BRep.make_solid`.
* Added `compas_occ.brep.BRep.centroid`.
* Added `compas_occ.brep.BRep.volume`.
* Added `compas_occ.brep.BRep.shells`.
* Added `compas_occ.brep.BRep.solids`.
* Added `compas_occ.brep.BRep.is_shell`.
* Added `compas_occ.brep.BRep.is_solid`.
* Added `compas_occ.brep.BRep.slice`.
* Added `compas_occ.brep.BRep.split`.
* Added `compas_occ.brep.BRepFace.data`.
* Added `compas_occ.brep.BRepLoop.data`.
* Added `compas_occ.brep.BRepEdge.data`.
* Added `compas_occ.brep.BRepVertex.data`.
* Added `compas_occ.brep.BRep.area`.
* Added `compas_occ.brep.BRepEdge.length`.
* Added `compas_occ.brep.BRep.vertex_neighbors`.
* Added `compas_occ.brep.BRep.vertex_edges`.
* Added `compas_occ.brep.BRep.vertex_faces`.
* Added `compas_occ.brep.BRep.from_sweep`.
* Added nurbs conversion to `compas_occ.brep.BRepEdge.data`.
* Added nurbs conversion to `compas_occ.brep.BRepFace.data`.

### Changed

* Fixed unused precision parameter in `compas_occ.geometry.OCCCurve.length`.
* Fixed bug in `compas_occ.brep.BRep.to_meshes`.
* Changed `compas_frame_from_occ_position` to `compas_frame_from_occ_ax3`.
* Changed `compas_occ.brep.BRep.to_tesselation` to use `BRepMesh_IncrementalMesh`.
* Changed base of `compas_occ.brep.BRepVertex`, `compas_occ.brep.BRepEdge`, `compas_occ.brep.BRepLoop`, `compas_occ.brep.BRepFace`, `compas_occ.brep.BRep` to `compas.data.Data`.
* Changed conversion functions (`compas_occ.conversions`) to take optional COMPAS type parameter.
* Changed `compas_occ.brep.BRep.data` to use component data.

### Removed

## [0.4.2] 2022-03-22

### Added

* Added `compas_occ.geometry.OCCNurbsCurve.join`.
* Added `compas_occ.geometry.OCCNurbsCurve.joined`.

### Changed

* Extend `compas_occ.geometry.OCCNurbsSurface.from_fill` with up to 4 input curves.

### Removed

## [0.4.1] 2022-03-22

### Added

### Changed

### Removed

## [0.4.0] 2022-02-07

### Added

* Added `compas_occ.geometry.OCCCurve`.
* Added `compas_occ.geometry.OCCSurface`.
* Added `compas_occ.brep.BRep.__add__` to support boolean union through "+".
* Added `compas_occ.brep.BRep.__sub__` to support boolean difference through "-".
* Added `compas_occ.brep.BRep.__and__` to support boolean intersection through "&".

### Changed

* Changed base class of `compas_occ.geometry.OCCNurbsCurve` to `compas_occ.geometry.OCCCurve`.
* Changed base class of `compas_occ.geometry.OCCNurbsSurface` to `compas_occ.geometry.OCCSurface`.
* Changed `compas_occ.brep.BRepEdge` to use `compas_occ.geometry.OCCCurve`.
* Fixed bug in `compas_occ.brep.BRep.to_meshes`.
* Fixed registration of curve plugin constructors to support multiple inheritance.
* Fixed registration of surface plugin constructors to support multiple inheritance.
* Fixed `compas_occ.geometry.NurbsCurve.copy`.

### Removed

## [0.3.4] 2022-01-17

### Added

### Changed

* Fixed input parameters and docstring of `compas_occ.geometry.NurbsSurface.closest_point`.
* Fixed bug in `compas_occ.geometry.NurbsCurve.transform`.

### Removed

## [0.3.3] 2021-12-16

### Added

### Changed

### Removed

## [0.3.2] 2021-12-14

### Added

* Added `compas_occ.brep.BRep`.
* Added `compas_occ.brep.BRepEdge`.
* Added `compas_occ.brep.BRepFace`.
* Added `compas_occ.brep.BRepLoop`.
* Added `compas_occ.brep.BRepVertex`.
* Added `compas_occ.geometry.NurbsCurve.segment`.
* Added `compas_occ.geometry.NurbsCurve.segmented`.
* Added `compas_occ.geometry.NurbsCurve.closest_point`.
* Added `compas_occ.geometry.NurbsCurve.curve_closest_parameters`.

### Changed

* Fixed input parameters of `new_nurbscurve_from_interpolation`.
* Fixed input parameters of `new_nurbscurve_from_step`.
* Fixed error in attributes of empty curve.
* Fixed error in parameter list of `new_nurbscurve` plugin.
* Fixed exception handling in `compas_occ.geometry.NurbsCurve.closest_point` if no orthogonal projection possible.

### Removed
