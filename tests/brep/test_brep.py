from pytest import fixture

from compas.geometry import Box

from compas_occ.brep import BRep


@fixture
def box():
    return Box.from_width_height_depth(5., 5., 5.,)


def test_create_brep():
    _ = BRep()


def test_brep_from_box(box):
    _ = BRep.from_box(box)


def test_brep_from_box_properties(box):
    brep = BRep.from_box(box)
    _ = brep.frame
