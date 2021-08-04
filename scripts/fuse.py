from compas.geometry import Box, Translation
from compas_occ.brep import BRep

A = BRep.from_box(Box.from_width_height_depth(1, 1, 1))
B = BRep.from_box(Box.from_width_height_depth(1, 1, 1).transformed(Translation.from_vector([0.5, 0, 1])))

print(A.type)

C = BRep.from_boolean_union(A, B)

print(C.type)

C.to_step('c.stp')
