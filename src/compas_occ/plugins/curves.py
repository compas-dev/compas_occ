"""Curve plugin registrations for COMPAS."""

from compas.plugins import plugin


@plugin(category="factories", requires=["OCC"])
def curve_from_native(cls, *args, **kwargs):
    from compas_occ.geometry import OCCCurve

    return OCCCurve.from_native(*args, **kwargs)


def _occ(curve):
    from compas_occ.geometry import OCCNurbsCurve

    return OCCNurbsCurve.from_native(curve.native_curve)


def _wrap(curve):
    from compas.geometry import NurbsCurve

    return NurbsCurve(native_curve=curve.native_curve)


def _new(method, *args, **kwargs):
    from compas_occ.geometry import OCCNurbsCurve

    return _wrap(getattr(OCCNurbsCurve, method)(*args, **kwargs))


@plugin(category="nurbscurve-factories", requires=["OCC"])
def from_native(*args, **kwargs):
    return _new("from_native", *args, **kwargs)


@plugin(category="nurbscurve-factories", requires=["OCC"])
def from_interpolation(*args, **kwargs):
    return _new("from_interpolation", *args, **kwargs)


@plugin(category="nurbscurve-factories", requires=["OCC"])
def from_parameters(*args, **kwargs):
    return _new("from_parameters", *args, **kwargs)


@plugin(category="nurbscurve-factories", requires=["OCC"])
def from_points(*args, **kwargs):
    return _new("from_points", *args, **kwargs)


@plugin(category="nurbscurve-io", requires=["OCC"])
def from_step(filepath):
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.Geom import Geom_TrimmedCurve
    from OCC.Core.GeomConvert import geomconvert

    from compas.geometry import NurbsCurve
    from compas_occ.brep import OCCBrep

    brep = OCCBrep.from_step(filepath, solid=False)
    if not brep.edges:
        raise ValueError("The STEP file does not contain a curve.")
    curve, first, last = BRep_Tool.Curve(brep.edges[0].occ_edge)
    native_curve = geomconvert.CurveToBSplineCurve(Geom_TrimmedCurve(curve, first, last))
    return NurbsCurve(native_curve=native_curve)


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_points(curve):
    return _occ(curve).points


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_weights(curve):
    return _occ(curve).weights


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_knots(curve):
    return _occ(curve).knots


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_multiplicities(curve):
    return _occ(curve).multiplicities


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_continuity(curve):
    return _occ(curve).continuity


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_degree(curve):
    return _occ(curve).degree


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_is_rational(curve):
    return _occ(curve).is_rational


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_domain(curve):
    return _occ(curve).domain


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_length(curve):
    return _occ(curve).length()


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_is_closed(curve):
    return _occ(curve).is_closed


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_is_periodic(curve):
    return _occ(curve).is_periodic


@plugin(category="nurbscurve-evaluation", requires=["OCC"])
def curve_point_at(curve, t, world=True):
    return _occ(curve).point_at(t)


@plugin(category="nurbscurve-evaluation", requires=["OCC"])
def curve_normal_at(curve, t, world=True):
    occ_curve = _occ(curve)
    curvature = occ_curve.curvature_at(t)
    if not curvature.length:
        return None
    return occ_curve.frame_at(t).yaxis


@plugin(category="nurbscurve-evaluation", requires=["OCC"])
def curve_tangent_at(curve, t, world=True):
    return _occ(curve).tangent_at(t)


@plugin(category="nurbscurve-evaluation", requires=["OCC"])
def curve_curvature_at(curve, t):
    return _occ(curve).curvature_at(t)


@plugin(category="nurbscurve-operations", requires=["OCC"])
def curve_transform(curve, transformation):
    _occ(curve).transform(transformation)


@plugin(category="nurbscurve-operations", requires=["OCC"])
def curve_reverse(curve):
    _occ(curve).reverse()


@plugin(category="nurbscurve-operations", requires=["OCC"])
def curve_closest_point(curve, point, return_parameter=False):
    return _occ(curve).closest_point(point, return_parameter=return_parameter)


@plugin(category="nurbscurve-operations", requires=["OCC"])
def curve_divide_by_count(curve, count, return_points=False):
    return _occ(curve).divide_by_count(count, return_points=return_points)


@plugin(category="nurbscurve-operations", requires=["OCC"])
def curve_divide_by_length(curve, length, return_points=False):
    return _occ(curve).divide_by_length(length, return_points=return_points)


@plugin(category="nurbscurve-io", requires=["OCC"])
def curve_to_step(curve, filepath, schema="AP203"):
    _occ(curve).to_step(str(filepath), schema=schema)
