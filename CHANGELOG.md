# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

* Added `compas_occ.brep.BRep`.
* Added `compas_occ.brep.BRepEdge`.
* Added `compas_occ.brep.BRepFace`.
* Added `compas_occ.brep.BRepLoop`.
* Added `compas_occ.brep.BRepVertex`.
* Added `compas_occ.geometry.NurbsCurve.segment`.
* Added `compas_occ.geometry.NurbsCurve.segmented`.
* Added `compas_occ.geometry.NurbsCurve.closest_point`.
* Added `compas_occ.geometry.NurbsCurve.closest_parameters_curve`.

### Changed

* Fixed input parameters of `new_nurbscurve_from_interpolation`.
* Fixed input parameters of `new_nurbscurve_from_step`.
* Fixed error in attributes of empty curve.
* Fixed error in parameter list of `new_nurbscurve` plugin.

### Removed
