from pytest import fixture

from compas.geometry import Box, Frame
from compas.geometry import close

from compas_occ.brep import BRep


@fixture
def box():
    return Box.from_width_height_depth(5., 5., 5.,)


def test_create_brep():
    brep = BRep()
    assert brep is not None


def test_brep_from_box(box):
    box_brep = BRep.from_box(box)
    assert close(box_brep.volume, box.volume)
    assert close(box_brep.area, box.area)


def test_brep_from_box_properties(box):
    brep = BRep.from_box(box)
    assert brep.frame == Frame.worldXY()
