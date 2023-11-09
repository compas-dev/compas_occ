# type: ignore

import os
from compas_view2.app import App
from compas.brep import Brep

brep = Brep.from_step(os.path.join(os.path.dirname(__file__), "FCA.stp"))
letters = list(brep.solids)

for letter in letters:
    letter.heal()
    letter.make_solid()

    exclude = []
    for loop in letter.loops:
        do_fillet = True
        for edge in loop.edges:
            for vertex in edge.vertices:
                if any(e.length < 0.01 for e in letter.vertex_edges(vertex)):
                    do_fillet = False
                    break
            if not do_fillet:
                break
        if not do_fillet:
            for vertex in loop.vertices:
                for edge in letter.vertex_edges(vertex):
                    exclude.append(edge)

    letter.fillet(0.1, exclude=exclude)

viewer = App()
viewer.view.camera.position = [5, -1, 10]
viewer.view.camera.look_at([5, 2, 0])

for letter in letters:
    viewer.add(letter, linewidth=2, opacity=0.7)
viewer.run()
