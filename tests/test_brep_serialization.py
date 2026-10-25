import copy

import compas
import pytest
from compas.geometry import Box
from compas.geometry import Brep
from compas.geometry import Circle
from compas.geometry import Plane

from compas_occ.brep import OCCBrep
from compas_occ.brep import OCCBrepEdge
from compas_occ.brep import OCCBrepFace
from compas_occ.brep import OCCBrepLoop


def test_neutral_schema_is_versioned_and_native_payload_is_opt_in():
    data = OCCBrep.from_box(Box(1)).to_data(units="MM")

    assert data["schema"] == "compas.brep"
    assert data["version"] == 1
    assert data["units"] == "MM"
    assert data["geometry"] == {"representation": "embedded"}
    assert data["topology"]["representation"] == "components"
    assert len(data["topology"]["components"]) == 1
    assert len(data["topology"]["components"][0]["faces"]) == 6
    assert "native" not in data


def test_native_payload_has_explicit_backend_format_and_encoding():
    data = OCCBrep.from_box(Box(1)).to_data(include_native=True)

    assert data["native"]["backend"] == "occ"
    assert data["native"]["format"] == "brep"
    assert data["native"]["encoding"] == "base64"
    assert isinstance(data["native"]["data"], str)
    assert data["native"]["data"]


def test_native_roundtrip_preserves_shape_without_healing():
    original = OCCBrep.from_box(Box(1, 2, 3))

    restored = OCCBrep.from_data(original.to_data(include_native=True))

    assert restored.is_valid
    assert restored.is_solid
    assert len(restored.faces) == 6
    assert restored.volume == pytest.approx(original.volume)


def test_neutral_roundtrip_can_explicitly_heal_reconstructed_topology():
    original = OCCBrep.from_box(Box(1, 2, 3))

    restored = OCCBrep.from_data(original.to_data(), prefer_native=False, heal=True)

    assert restored.is_valid
    assert restored.is_solid
    assert restored.volume == pytest.approx(original.volume)


def test_neutral_roundtrip_preserves_inner_boundaries():
    boundary = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(Circle(2.0))])
    hole = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(Circle(0.5))])
    face = OCCBrepFace.from_plane(Plane.worldXY(), boundary=boundary, holes=[hole])
    original = OCCBrep.from_brepfaces([face], solid=False)

    restored = OCCBrep.from_data(original.to_data(), prefer_native=False, heal=True)

    assert restored.is_valid
    assert len(restored.faces) == 1
    assert len(restored.faces[0].innerloops) == 1
    assert restored.area == pytest.approx(original.area)


def test_neutral_roundtrip_preserves_multiple_solid_components():
    first = OCCBrep.from_box(Box(1))
    second = OCCBrep.from_box(Box(2))
    original = OCCBrep.from_breps([first, second])

    restored = OCCBrep.from_data(original.to_data(), prefer_native=False, heal=True)

    assert restored.is_valid
    assert restored.is_compound
    assert len(restored.solids) == 2
    assert len(restored.faces) == 12


def test_standard_occ_json_uses_exact_native_payload():
    original = OCCBrep.from_box(Box(1))

    encoded = compas.json_dumps(original)
    restored = compas.json_loads(encoded)

    assert '"native"' in encoded
    assert type(restored) is OCCBrep
    assert restored.is_valid
    assert restored.volume == pytest.approx(original.volume)


def test_stable_brep_json_uses_serialization_plugins():
    original = Brep.from_box(Box(1))

    restored = Brep.from_jsonstring(original.to_jsonstring())

    assert type(restored) is Brep
    assert restored.is_valid
    assert restored.volume == pytest.approx(original.volume)


def test_legacy_face_data_remains_loadable():
    original = OCCBrep.from_box(Box(1))
    versioned = original.to_data()
    legacy = {"faces": versioned["topology"]["components"][0]["faces"]}

    restored = OCCBrep.from_data(legacy, prefer_native=False, heal=True)

    assert restored.is_valid
    assert restored.is_solid
    assert restored.volume == pytest.approx(original.volume)


def test_prefer_native_ignores_unusable_neutral_topology():
    original = OCCBrep.from_box(Box(1))
    data = original.to_data(include_native=True)
    data["topology"]["components"] = []

    restored = OCCBrep.from_data(data)

    assert restored.is_valid
    assert restored.volume == pytest.approx(original.volume)


def test_disabling_native_payload_ignores_malformed_native_data():
    original = OCCBrep.from_box(Box(1))
    data = original.to_data(include_native=True)
    data["native"]["data"] = "not base64"

    restored = OCCBrep.from_data(data, prefer_native=False, heal=True)

    assert restored.is_valid
    assert restored.volume == pytest.approx(original.volume)


@pytest.mark.parametrize(
    "change, message",
    [
        ({"schema": "other.brep"}, "Unsupported BRep schema"),
        ({"version": 99}, "Unsupported BRep schema version"),
        ({"topology": {"representation": "faces", "faces": []}}, "component-oriented topology"),
        ({"topology": {"representation": "components", "components": "invalid"}}, "components should be a list"),
    ],
)
def test_unsupported_or_malformed_neutral_schema_is_rejected(change, message):
    data = OCCBrep.from_box(Box(1)).to_data()
    data.update(change)

    with pytest.raises(ValueError, match=message):
        OCCBrep.from_data(data, prefer_native=False)


@pytest.mark.parametrize(
    "native",
    [
        {"backend": "other", "format": "brep", "encoding": "base64", "data": ""},
        {"backend": "occ", "format": "step", "encoding": "base64", "data": ""},
        {"backend": "occ", "format": "brep", "encoding": "text", "data": ""},
    ],
)
def test_unsupported_native_payload_is_rejected(native):
    data = OCCBrep.from_box(Box(1)).to_data()
    data["native"] = native

    with pytest.raises(ValueError, match="Unsupported native BRep payload"):
        OCCBrep.from_data(data)


def test_malformed_base64_native_payload_is_rejected():
    data = OCCBrep.from_box(Box(1)).to_data(include_native=True)
    data["native"]["data"] = "not base64"

    with pytest.raises(ValueError, match="not valid Base64"):
        OCCBrep.from_data(data)


def test_input_data_is_not_mutated_during_deserialization():
    data = OCCBrep.from_box(Box(1)).to_data(include_native=True)
    before = copy.deepcopy(data)

    OCCBrep.from_data(data)

    assert data == before


@pytest.mark.parametrize("data", [None, [], "brep"])
def test_non_mapping_data_is_rejected(data):
    with pytest.raises(TypeError, match="dictionary"):
        OCCBrep.from_data(data)
