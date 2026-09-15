from pathlib import Path

from compas_viewer import Viewer

from compas_occ.brep import OCCBrep

# Load the brep from a STEP file
# and extract the individual letters.

filepath = Path(__file__).parent / "FCA.stp"
brep = OCCBrep.from_step(filepath)
letters = list(brep.solids)

# Make sure the letters are valid solids.

for letter in letters:
    letter.heal()
    letter.make_solid()

# For each letter, exclude the edges that are too short and the edges connected to it,
# and fillet the rest.

for letter in letters:
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

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [5, 2, 0]
viewer.renderer.camera.position = [5, -1, 10]

for letter in letters:
    viewer.scene.add(letter, linewidth=2, opacity=0.7, show_points=False)

viewer.show()
