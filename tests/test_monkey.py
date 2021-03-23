from OCCUtils import Topo
from OCCUtils.Common import vertex2pnt
from compas.geometry import Box, Translation

from compas_occ.shapes.monkey import Frame


def test_frame(frame: Frame):
    """ round trip test of compas.geometry.Frame -> OCC.gp.gp_Ax3 -> compas.geometry.Frame

    test vector / point / direction conversion implicitly

     """
    occ_frame = frame.to_occ()
    print(occ_frame)
    compas_frame = occ_frame.to_compas()
    # round trip compas -> occ -> compas
    assert frame == compas_frame


def test_box(box: Box):
    occ_box = box.to_occ()
    # check on the vertex level
    verts = [i.to_occ() for i in box.vertices]
    topo = Topo(occ_box)
    verts_occ = [vertex2pnt(i) for i in topo.vertices()]

    check = []
    for a in verts:
        for b in verts_occ:
            if a.IsEqual(b, 1e-3):
                check.append(True)
                break

    assert len(check) == len(verts)
    # converting the TopoDS_Solid -> compas.geometry.Box seems futile for now...
