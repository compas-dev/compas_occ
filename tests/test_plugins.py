from importlib.metadata import EntryPoint
import sys

import pytest
from compas.plugins import ExtensionPoint
from compas.plugins import PluginManager


def test_entry_point_exposes_factory_plugins():
    entry_points = [
        EntryPoint(name="compas_occ_brep", value="compas_occ.plugins.brep", group="compas.plugins"),
        EntryPoint(name="compas_occ_curves", value="compas_occ.plugins.curves", group="compas.plugins"),
        EntryPoint(name="compas_occ_intersections", value="compas_occ.plugins.intersections", group="compas.plugins"),
        EntryPoint(name="compas_occ_surfaces", value="compas_occ.plugins.surfaces", group="compas.plugins"),
    ]
    manager = PluginManager(entry_points_provider=lambda *, group: entry_points)
    occ_modules = {name for name in sys.modules if name == "OCC" or name.startswith("OCC.")}

    assert manager.load_plugins() == 108
    assert {name for name in sys.modules if name == "OCC" or name.startswith("OCC.")} == occ_modules
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-factories", "from_box") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-operations", "from_boolean_union") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "nurbscurve-factories", "from_points") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "nurbssurface-factories", "from_points") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "nurbssurface-queries", "surface_points") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-queries", "brep_area") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "brep-io", "brep_to_step") in manager.registry
    assert ExtensionPoint("https://plugins.compas.dev/", "intersections", "intersection_surface_brep") in manager.registry


def test_brep_plugins_use_stable_wrapper():
    from compas.geometry import Box
    from compas.geometry import Brep

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

    restored = Brep.from_jsonstring(brep.to_jsonstring())
    assert type(restored) is Brep
    assert restored.is_valid
    assert restored.volume == pytest.approx(brep.volume)
