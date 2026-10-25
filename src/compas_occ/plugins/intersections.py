"""Intersection plugin registrations for COMPAS."""

from compas.plugins import plugin


def _register(name):
    def intersection(*args, **kwargs):
        from compas_occ import intersections

        return getattr(intersections, name)(*args, **kwargs)

    intersection.__name__ = name
    return plugin(category="intersections", requires=["OCC"])(intersection)


intersection_line_surface = _register("intersection_line_surface")
intersection_plane_surface = _register("intersection_plane_surface")
intersection_curve_surface = _register("intersection_curve_surface")
intersection_surface_surface = _register("intersection_surface_surface")
intersection_line_brep = _register("intersection_line_brep")
intersection_plane_brep = _register("intersection_plane_brep")
intersection_curve_brep = _register("intersection_curve_brep")
intersection_surface_brep = _register("intersection_surface_brep")
