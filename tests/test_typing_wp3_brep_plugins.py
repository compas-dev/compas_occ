import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

from compas.geometry import Box
from compas.geometry.brep import operations as core_brep
from compas_occ.brep import OCCBrep
from compas_occ.plugins import brep as occ_brep


ROOT = Path(__file__).parents[1]


def test_registered_brep_plugin_signatures_match_core_contracts():
    registered = {name: function for name, function in vars(occ_brep).items() if callable(function) and hasattr(function, "__plugin_spec__")}

    assert len(registered) == 63
    for name, function in registered.items():
        assert inspect.signature(function) == inspect.signature(getattr(core_brep, name)), name


def test_brep_plugin_typing_fixture_has_no_diagnostics():
    fixture = ROOT / "tests" / "typing" / "brep_plugins_wp3.py"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pyright",
            "--outputjson",
            "--pythonpath",
            sys.executable,
            str(fixture),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode in {0, 1}, result.stderr
    assert json.loads(result.stdout)["generalDiagnostics"] == []


def test_brep_factories_forward_defaults_and_arguments(monkeypatch):
    calls = []

    def capture(method, *args, **kwargs):
        calls.append((method, args, kwargs))
        return object()

    monkeypatch.setattr(occ_brep, "_factory", capture)
    plane = object()
    curve = object()
    vector = object()

    occ_brep.from_plane(plane)
    occ_brep.from_extrusion(curve, vector)

    assert calls == [
        ("from_plane", (plane,), {"domain_u": (-1, 1), "domain_v": (-1, 1)}),
        ("from_extrusion", (curve, vector), {"cap_ends": True}),
    ]


def test_brep_overlap_forwards_options_and_preserves_pair_structure(monkeypatch):
    expected = ([object()], [object()])

    class FakeBrep:
        def overlap(self, other, **kwargs):
            assert other == "other-occ"
            assert kwargs == {
                "linear_deflection": 0.1,
                "angular_deflection": 0.2,
                "tolerance": 0.3,
                "relative": True,
            }
            return expected

    def capture_occ(value):
        return FakeBrep() if value == "first" else "other-occ"

    monkeypatch.setattr(occ_brep, "_occ", capture_occ)

    result = occ_brep.brep_overlap(
        "first",
        "second",
        linear_deflection=0.1,
        angular_deflection=0.2,
        tolerance=0.3,
        relative=True,
    )

    assert result is expected


def test_brep_tessellation_forwards_concrete_public_units(monkeypatch):
    captured = {}

    class FakeBrep:
        def to_tessellation(self, *, linear_deflection, angular_deflection):
            captured.update(
                linear_deflection=linear_deflection,
                angular_deflection=angular_deflection,
            )
            return "tessellation"

    monkeypatch.setattr(occ_brep, "_occ", lambda brep: FakeBrep())

    result = occ_brep.brep_to_tessellation(
        object(),
        linear_deflection=0.01,
        angular_deflection=12.0,
    )

    assert result == "tessellation"
    assert captured == {
        "linear_deflection": 0.01,
        "angular_deflection": 12.0,
    }


def test_removed_brep_conversion_hooks_are_absent():
    assert not hasattr(occ_brep, "brep_tessellate")
    assert not hasattr(occ_brep, "brep_polygonize")


def test_brep_fillet_materializes_excluded_edge_sequence_once(monkeypatch):
    excluded = (edge for edge in [object(), object()])
    captured = {}

    class FakeBrep:
        def filleted(self, radius, exclude=None):
            captured.update(radius=radius, exclude=exclude)
            return object()

    monkeypatch.setattr(occ_brep, "_occ", lambda brep: FakeBrep())
    monkeypatch.setattr(occ_brep, "_wrap", lambda brep: brep)

    occ_brep.brep_fillet(object(), 2.5, exclude=excluded)

    assert captured["radius"] == 2.5
    assert isinstance(captured["exclude"], list)
    assert len(captured["exclude"]) == 2


def test_supported_brep_queries_are_independent(monkeypatch):
    from OCC.Core.TopAbs import TopAbs_FACE

    vertex = object()
    edge = object()
    loop = object()
    face = object()
    shell = object()
    solid = object()

    class FakeBrep:
        orientation = 0
        type = TopAbs_FACE
        is_valid = True
        is_compound = False
        is_compoundsolid = False
        is_shell = False
        is_solid = True
        vertices = [vertex]
        edges = [edge]
        loops = [loop]
        faces = [face]
        shells = [shell]
        solids = [solid]

    monkeypatch.setattr(occ_brep, "_occ", lambda brep: FakeBrep())
    monkeypatch.setattr(occ_brep, "_wrap", lambda item: ("wrapped", item))

    assert occ_brep.brep_orientation(object()) == 0
    assert occ_brep.brep_type(object()) == int(TopAbs_FACE)
    assert occ_brep.brep_is_valid(object()) is True
    assert occ_brep.brep_is_compound(object()) is False
    assert occ_brep.brep_is_compoundsolid(object()) is False
    assert occ_brep.brep_is_shell(object()) is False
    assert occ_brep.brep_is_solid(object()) is True
    assert occ_brep.brep_is_surface(object()) is True
    assert occ_brep.brep_vertices(object()) == [vertex]
    assert occ_brep.brep_edges(object()) == [edge]
    assert occ_brep.brep_loops(object()) == [loop]
    assert occ_brep.brep_faces(object()) == [face]
    assert occ_brep.brep_shells(object()) == [("wrapped", shell)]
    assert occ_brep.brep_solids(object()) == [("wrapped", solid)]


@pytest.mark.parametrize(
    "query",
    [
        occ_brep.brep_is_orientable,
        occ_brep.brep_is_closed,
        occ_brep.brep_is_infinite,
        occ_brep.brep_is_convex,
        occ_brep.brep_is_manifold,
        occ_brep.brep_trims,
    ],
)
def test_unsupported_brep_queries_fail_explicitly(query):
    with pytest.raises(NotImplementedError):
        query(object())


def test_occ_brep_properties_do_not_expose_unknown_native_flags():
    brep = OCCBrep.from_box(Box(1))

    assert brep.is_valid is True
    assert brep.is_solid is True
    assert brep.is_surface is False

    for name in ["is_orientable", "is_closed", "is_infinite", "is_convex", "is_manifold"]:
        with pytest.raises(NotImplementedError):
            getattr(brep, name)
