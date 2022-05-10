# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

* Added `compas_occ.geometry.OCCRevolutionSurface`.
* Added `compas_occ.conversions.compas_axis_to_occ_axis`.
* Added `compas_occ.conversions.compas_axis_from_occ_axis`.
* Added `compas_occ.geometry.OCCExtrusionSurface`.
* Added `compas_occ.geometry.OCCNurbsSurface.from_extrusion`.
* Added implementation for `compas_occ.geometry.OCCCurve.divide_by_count`.
* Added `compas_occ.geometry.OCCCurve.divide` as alias for `compas_occ.geometry.OCCCurve.divide_by_count`.
* Added `compas_occ.geometry.OCCCurve.projected`.
* Added `compas_occ.geometry.OCCCurve.embedded`.
* Added `compas_occ.brep.BRep.from_faces`.
* Added `compas_occ.brep.BRep.from_polygons`.
* Added `compas_occ.brep.BRep.check`.
* Added `compas_occ.brep.BRep.sew`.
* Added `compas_occ.brep.BRep.fix`.

### Changed

* Fixed unused precision parameter in `compas_occ.geometry.OCCCurve.length`.
* Fixed bug in `compas_occ.brep.BRep.to_meshes`.
* Changed `compas_frame_from_occ_position` to `compas_frame_from_occ_ax3`.
* Changed `compas_occ.brep.BRep.to_tesselation` to use `BRepMesh_IncrementalMesh`.
* Changes base of `compas_occ.brep.BRepVertex`, `compas_occ.brep.BRepEdge`, `compas_occ.brep.BRepLoop`, `compas_occ.brep.BRepFace`, `compas_occ.brep.BRep` to `compas.data.Data`.

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
