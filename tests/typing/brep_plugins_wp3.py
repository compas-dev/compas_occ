from typing import Any
from typing import Literal
from typing import assert_type
from typing import cast

from compas.geometry import Box
from compas.geometry import Brep
from compas.geometry import BrepEdge
from compas.geometry import BrepFace
from compas.geometry import BrepLoop
from compas.geometry import BrepTrim
from compas.geometry import BrepVertex
from compas_occ.plugins.brep import brep_area
from compas_occ.plugins.brep import brep_edges
from compas_occ.plugins.brep import brep_faces
from compas_occ.plugins.brep import brep_is_closed
from compas_occ.plugins.brep import brep_loops
from compas_occ.plugins.brep import brep_orientation
from compas_occ.plugins.brep import brep_overlap
from compas_occ.plugins.brep import brep_shells
from compas_occ.plugins.brep import brep_solids
from compas_occ.plugins.brep import brep_to_data
from compas_occ.plugins.brep import brep_trims
from compas_occ.plugins.brep import brep_type
from compas_occ.plugins.brep import brep_vertices
from compas_occ.plugins.brep import from_box
from compas_occ.plugins.brep import from_native


brep = cast(Brep, object())

assert_type(from_box(Box(1)), Brep)
assert_type(from_native(cast(Any, object())), Brep)
assert_type(brep_area(brep), float)
assert_type(brep_to_data(brep), dict[str, Any])
assert_type(brep_orientation(brep), Literal[0, 1, 2, 3])
assert_type(brep_type(brep), Literal[0, 1, 2, 3, 4, 5, 6, 7, 8])
assert_type(brep_is_closed(brep), bool)
assert_type(brep_vertices(brep), list[BrepVertex])
assert_type(brep_edges(brep), list[BrepEdge])
assert_type(brep_trims(brep), list[BrepTrim])
assert_type(brep_loops(brep), list[BrepLoop])
assert_type(brep_faces(brep), list[BrepFace])
assert_type(brep_shells(brep), list[Brep])
assert_type(brep_solids(brep), list[Brep])
assert_type(brep_overlap(brep, brep), tuple[list[BrepFace], list[BrepFace]])
