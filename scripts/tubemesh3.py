import os
import compas
from compas.datastructures import Mesh

from compas_occ.brep.datastructures import BRepShape
from compas_occ.interop.meshes import compas_quadmesh_to_occ_shell

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '__tubemesh.stp')

mesh = Mesh.from_obj(compas.get('tubemesh.obj'))

shell = compas_quadmesh_to_occ_shell(mesh)

shape = BRepShape(shell)
shape.to_step(FILE)
