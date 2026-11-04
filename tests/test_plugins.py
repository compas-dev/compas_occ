from importlib.metadata import EntryPoint
import inspect
import sys

import pytest
from compas.plugins import ExtensionPoint
from compas.plugins import PluginManager


INTERSECTION_PLUGIN_NAMES = [
    "intersection_line_surface",
    "intersection_plane_surface",
    "intersection_curve_surface",
    "intersection_surface_surface",
    "intersection_line_brep",
    "intersection_plane_brep",
    "intersection_curve_brep",
    "intersection_surface_brep",
]


def test_entry_point_exposes_factory_plugins():
    entry_points = [
        EntryPoint(name="compas_occ_brep", value="compas_occ.plugins.brep", group="compas.plugins"),
        EntryPoint(name="compas_occ_curves", value="compas_occ.plugins.curves", group="compas.plugins"),
        EntryPoint(name="compas_occ_intersections", value="compas_occ.plugins.intersections", group="compas.plugins"),
        EntryPoint(name="compas_occ_surfaces", value="compas_occ.plugins.surfaces", group="compas.plugins"),
    ]
    manager = PluginManager(entry_points_provider=lambda *, group: entry_points)
    occ_modules = {name for name in sys.modules if name == "OCC" or name.startswith("OCC.")}

    assert manager.load_plugins() == 113
    assert {name for name in sys.modules if name == "OCC" or name.startswith("OCC.")} == occ_modules
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-factories", "from_box") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-operations", "from_boolean_union") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "nurbscurve-factories", "from_points") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "nurbssurface-factories", "from_points") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "nurbssurface-queries", "surface_points") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-queries", "brep_area") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-queries", "brep_aabb") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-queries", "brep_obb") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-operations", "brep_tessellate") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-operations", "brep_polygonize") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-operations", "brep_copy") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-operations", "brep_transform") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-io", "brep_to_step") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "intersections", "intersection_surface_brep") in manager.registry


@pytest.mark.parametrize("name", INTERSECTION_PLUGIN_NAMES)
def test_intersection_plugin_signature_matches_core_pluggable(name):
    from compas.geometry import intersections as core_intersections
    from compas_occ.plugins import intersections as occ_intersections

    core_signature = inspect.signature(getattr(core_intersections, name))
    plugin_signature = inspect.signature(getattr(occ_intersections, name))

    assert tuple(plugin_signature.parameters) == tuple(core_signature.parameters)
    for plugin_parameter, core_parameter in zip(plugin_signature.parameters.values(), core_signature.parameters.values()):
        assert plugin_parameter.kind == core_parameter.kind
        assert plugin_parameter.default == core_parameter.default
        assert plugin_parameter.annotation == core_parameter.annotation
    assert plugin_signature.return_annotation == core_signature.return_annotation


def test_brep_plugins_use_stable_wrapper():
    from compas.geometry import Box
    from compas.geometry import Brep
    from compas.geometry import Deflection
    from compas.geometry import PolygonalSurface
    from compas.geometry import Tessellation

    brep = Brep.from_box(Box(1))

    assert type(brep) is Brep
    assert brep.is_valid
    assert brep.is_solid
    assert len(brep.vertices) == 8
    assert len(brep.edges) == 12
    assert len(brep.loops) == 6
    assert len(brep.faces) == 6
    assert brep.area == 6.0
    assert brep.volume == pytest.approx(1.0)

    strategy = Deflection(0.01, 12.0)
    tessellation = brep.tessellate(strategy)
    polygonal = brep.polygonize(strategy)

    assert isinstance(tessellation, Tessellation)
    assert isinstance(polygonal, PolygonalSurface)

    restored = Brep.from_jsonstring(brep.to_jsonstring())
    assert type(restored) is Brep
    assert restored.is_valid
    assert restored.volume == pytest.approx(brep.volume)


def test_brep_copy_and_transform_plugins():
    from compas.geometry import Box
    from compas.geometry import Brep
    from compas.geometry import Translation

    brep = Brep.from_box(Box(1))
    copied = brep.copy()

    assert type(copied) is Brep
    assert copied.native_brep is not brep.native_brep
    assert copied.volume == pytest.approx(brep.volume)
    assert copied.aabb.xsize == pytest.approx(1.0)
    assert copied.obb.xsize == pytest.approx(1.0)

    copied.transform(Translation.from_vector([1.0, 2.0, 3.0]))

    assert copied.centroid == [1.0, 2.0, 3.0]
    assert brep.centroid == [0.0, 0.0, 0.0]
