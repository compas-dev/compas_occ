from typing import List, Optional

import compas.geometry
import compas.datastructures

from compas.geometry import Frame
from compas.geometry import Transformation
from compas.geometry import Translation
from compas.datastructures import Mesh

from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Dir
from OCC.Core.gp import gp_Ax2

from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.TopoDS import TopoDS_Shape

from OCC.Core.TopExp import TopExp_Explorer

from OCC.Core.TopAbs import TopAbs_VERTEX
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.TopAbs import TopAbs_WIRE
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopAbs import TopAbs_Orientation
from OCC.Core.TopAbs import TopAbs_ShapeEnum

from OCC.Core.BRep import BRep_Builder

from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeSolid

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder

from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Common
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse

from OCC.Core.Tesselator import ShapeTesselator

from OCC.Core.STEPControl import STEPControl_Writer
from OCC.Core.STEPControl import STEPControl_AsIs
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone

from compas_occ.conversions import triangle_to_face
from compas_occ.conversions import quad_to_face
from compas_occ.conversions import ngon_to_face
from compas_occ.geometry import OCCNurbsSurface as NurbsSurface

from compas_occ.brep import BRepVertex
from compas_occ.brep import BRepEdge
from compas_occ.brep import BRepLoop
from compas_occ.brep import BRepFace


class BRep:
    """Class for Boundary Representation of geometric entities.

    Attributes
    ----------
    shape : :class:`TopoDS_Shape`
        The underlying OCC shape of the BRep.
    type : :class:`TopAbs_ShapeEnum`, read-only
        One of `{TopAbs_COMPOUND, TopAbs_COMPSOLID, TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE,  TopAbs_WIRE, TopAbs_EDGE, TopAbs_VERTEX, TopAbs_SHAPE}`.
    vertices : list of :class:`BRepVertex`, read-only
        The vertices of the BRep.
    edges : list of :class:`BRepEdge`, read-only
        The edges of the BRep.
    loops : list of :class:`BRepLoop`, read-only
        The loops of the BRep.
    faces : list of :class:`BRepFace`, read-only
        The faces of the BRep.
    orientation : :class:`TopAbs_Orientation`, read-only
        One of `{TopAbs_FORWARD, TopAbs_REVERSED, TopAbs_INTERNAL, TopAbs_EXTERNAL}`.
    frame : :class:`Frame`, read-only
        The local coordinate system of the BRep.
    area : float, read-only
        The surface area of the BRep.
    volume : float, read-only
        The volume of the regions contained by the BRep.
    """

    def __init__(self) -> None:
        self._shape = None

    # ==============================================================================
    # Customization
    # ==============================================================================

    # def __eq__(self, other):
    #     pass

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def shape(self) -> TopoDS_Shape:
        return self._shape

    @shape.setter
    def shape(self, shape: TopoDS_Shape) -> None:
        self._shape = shape

    @property
    def type(self) -> TopAbs_ShapeEnum:
        return self.shape.ShapeType()

    @property
    def vertices(self) -> List[BRepVertex]:
        vertices = []
        explorer = TopExp_Explorer(self.shape, TopAbs_VERTEX)
        while explorer.More():
            vertex = explorer.Current()
            vertices.append(BRepVertex(vertex))
            explorer.Next()
        return vertices

    @property
    def edges(self) -> List[BRepEdge]:
        edges = []
        explorer = TopExp_Explorer(self.shape, TopAbs_EDGE)
        while explorer.More():
            edge = explorer.Current()
            edges.append(BRepEdge(edge))
            explorer.Next()
        return edges

    @property
    def loops(self) -> List[BRepLoop]:
        loops = []
        explorer = TopExp_Explorer(self.shape, TopAbs_WIRE)
        while explorer.More():
            wire = explorer.Current()
            loops.append(BRepLoop(wire))
            explorer.Next()
        return loops

    @property
    def faces(self) -> List[BRepFace]:
        faces = []
        explorer = TopExp_Explorer(self.shape, TopAbs_FACE)
        while explorer.More():
            face = explorer.Current()
            faces.append(BRepFace(face))
            explorer.Next()
        return faces

    # trims
    # curves2D
    # curves3D
    # surfaces

    # regions
    # point inside (of solid brep)

    @property
    def orientation(self) -> TopAbs_Orientation:
        return self.shape.Orientation()

    @property
    def frame(self) -> compas.geometry.Frame:
        location = self.shape.Location()
        transformation = location.Transformation()
        T = Transformation(matrix=[[transformation.Value(i, j) for j in range(4)] for i in range(4)])
        frame = Frame.from_transformation(T)
        return frame

    @property
    def area(self) -> float:
        pass

    @property
    def volume(self) -> float:
        pass

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_corners(cls,
                     p1: compas.geometry.Point,
                     p2: compas.geometry.Point,
                     p3: compas.geometry.Point,
                     p4: Optional[compas.geometry.Point] = None) -> 'BRep':
        """Construct a BRep from 3 or 4 corner points."""
        if not p4:
            brep = BRep()
            brep.shape = triangle_to_face([p1, p2, p3])
            return brep
        brep = BRep()
        brep.shape = quad_to_face([p1, p2, p3, p4])
        return brep

    @classmethod
    def from_polygons(cls, polygons: List[compas.geometry.Polygon]) -> 'BRep':
        """Construct a BRep from a set of polygons."""
        shell = TopoDS_Shell()
        builder = BRep_Builder()
        builder.MakeShell(shell)
        for points in polygons:
            if len(points) == 3:
                builder.Add(shell, triangle_to_face(points))
            elif len(points) == 4:
                builder.Add(shell, quad_to_face(points))
            else:
                builder.Add(shell, ngon_to_face(points))
        brep = BRep()
        brep.shape = shell
        return brep

    @classmethod
    def from_curves(cls, curves) -> 'BRep':
        raise NotImplementedError

    @classmethod
    def from_box(cls, box: compas.geometry.Box) -> 'BRep':
        """Construct a BRep from a COMPAS box."""
        xaxis = box.frame.xaxis.scaled(-0.5 * box.xsize)
        yaxis = box.frame.yaxis.scaled(-0.5 * box.ysize)
        zaxis = box.frame.zaxis.scaled(-0.5 * box.zsize)
        frame = box.frame.transformed(Translation.from_vector(xaxis + yaxis + zaxis))
        ax2 = gp_Ax2(gp_Pnt(* frame.point), gp_Dir(* frame.zaxis), gp_Dir(* frame.xaxis))
        brep = BRep()
        brep.shape = BRepPrimAPI_MakeBox(ax2, box.xsize, box.ysize, box.zsize).Shape()
        return brep

    @classmethod
    def from_sphere(cls, sphere: compas.geometry.Sphere) -> 'BRep':
        """Construct a BRep from a COMPAS sphere."""
        brep = BRep()
        brep.shape = BRepPrimAPI_MakeSphere(gp_Pnt(* sphere.point), sphere.radius).Shape()
        return brep

    @classmethod
    def from_cylinder(cls, cylinder: compas.geometry.Cylinder) -> 'BRep':
        """Construct a BRep from a COMPAS cylinder."""
        plane = cylinder.circle.plane
        height = cylinder.height
        radius = cylinder.circle.radius
        frame = Frame.from_plane(plane)
        frame.transform(Translation.from_vector(frame.zaxis * (-0.5 * height)))
        ax2 = gp_Ax2(gp_Pnt(* frame.point), gp_Dir(* frame.zaxis), gp_Dir(* frame.xaxis))
        brep = BRep()
        brep.shape = BRepPrimAPI_MakeCylinder(ax2, radius, height).Shape()
        return brep

    @classmethod
    def from_cone(cls, cone: compas.geometry.Cone) -> 'BRep':
        """Construct a BRep from a COMPAS cone."""
        raise NotImplementedError

    @classmethod
    def from_torus(cls, torus: compas.geometry.Torus) -> 'BRep':
        """Construct a BRep from a COMPAS torus."""
        raise NotImplementedError

    @classmethod
    def from_boolean_difference(cls, A: 'BRep', B: 'BRep') -> 'BRep':
        """Construct a BRep from the boolean difference of two other BReps."""
        cut = BRepAlgoAPI_Cut(A.shape, B.shape)
        if not cut.IsDone():
            raise Exception("Boolean difference operation could not be completed.")
        brep = BRep()
        brep.shape = cut.Shape()
        return brep

    @classmethod
    def from_boolean_intersection(cls, A: 'BRep', B: 'BRep') -> 'BRep':
        """Construct a BRep from the boolean intersection of two other BReps."""
        common = BRepAlgoAPI_Common(A.shape, B.shape)
        if not common.IsDone():
            raise Exception("Boolean intersection operation could not be completed.")
        brep = BRep()
        brep.shape = common.Shape()
        return brep

    @classmethod
    def from_boolean_union(cls, A, B) -> 'BRep':
        """Construct a BRep from the boolean union of two other BReps."""
        fuse = BRepAlgoAPI_Fuse(A.shape, B.shape)
        if not fuse.IsDone():
            raise Exception("Boolean union operation could not be completed.")
        brep = BRep()
        brep.shape = fuse.Shape()
        return brep

    @classmethod
    def from_mesh(cls, mesh: compas.datastructures.Mesh) -> 'BRep':
        """Construct a BRep from a COMPAS mesh."""
        shell = TopoDS_Shell()
        builder = BRep_Builder()
        builder.MakeShell(shell)
        for face in mesh.faces():
            points = mesh.face_coordinates(face)
            if len(points) == 3:
                builder.Add(shell, triangle_to_face(points))
            elif len(points) == 4:
                builder.Add(shell, quad_to_face(points))
            else:
                builder.Add(shell, ngon_to_face(points))
        brep = BRep()
        brep.shape = shell
        return brep

    # create pipe
    # create patch
    # create offset

    # ==============================================================================
    # Converters
    # ==============================================================================

    def to_json(self, filepath: str):
        """Export the BRep to a JSON file."""
        with open(filepath, 'w') as f:
            self.shape.DumpJson(f)

    def to_step(self, filepath: str, schema: str = "AP203", unit: str = "MM") -> None:
        """Write the BRep shape to a STEP file."""
        step_writer = STEPControl_Writer()
        Interface_Static_SetCVal("write.step.schema", schema)
        Interface_Static_SetCVal("write.step.unit", unit)
        step_writer.Transfer(self.shape, STEPControl_AsIs)
        status = step_writer.Write(filepath)
        assert status == IFSelect_RetDone, "STEP writing failed."

    def to_tesselation(self) -> Mesh:
        """Create a tesselation of the shape for visualisation."""
        tesselation = ShapeTesselator(self.shape)
        tesselation.Compute()
        vertices = [tesselation.GetVertex(i) for i in range(tesselation.ObjGetVertexCount())]
        triangles = [tesselation.GetTriangleIndex(i) for i in range(tesselation.ObjGetTriangleCount())]
        return Mesh.from_vertices_and_faces(vertices, triangles)

    def to_meshes(self, u=16, v=16):
        """Convert the faces of the BRep shape to meshes."""
        converter = BRepBuilderAPI_NurbsConvert(self.shape, False)
        brep = BRep()
        brep.shape = converter.Shape()
        meshes = []
        for face in brep.faces:
            srf = NurbsSurface.from_face(face)
            mesh = srf.to_vizmesh(u, v)
            meshes.append(mesh)
        return meshes

    # make meshes from the loops
    # use gmsh to generate proper mesh

    def make_solid(self):
        self.shape = BRepBuilderAPI_MakeSolid(self.shape).Solid()

    # ==============================================================================
    # Methods
    # ==============================================================================

    def is_orientable(self) -> bool:
        """Check if the shape is orientable."""
        return self.shape.Orientable()

    def is_closed(self) -> bool:
        """Check if the shape is closed."""
        return self.shape.Closed()

    def is_infinite(self) -> bool:
        """Check if the shape is infinite."""
        return self.shape.Infinite()

    def is_convex(self) -> bool:
        """Check if the shape is convex."""
        return self.shape.Convex()

    def is_manifold(self) -> bool:
        pass

    def is_solid(self) -> bool:
        pass

    def is_surface(self) -> bool:
        pass

    def cull_unused_vertices(self) -> None:
        pass

    def cull_unused_edges(self) -> None:
        pass

    def cull_unused_loops(self) -> None:
        pass

    def cull_unused_faces(self) -> None:
        pass

    # flip
    # join
    # join edges
    # join naked edges
    # merge coplanar faces
    # remove fins
    # remove holes
    # repair
    # rotate
    # scale
    # split
    # trim
    # transform
    # rotate
    # translate
    # unjoin edges

    def contours(self, plane: compas.geometry.Plane, spacing: Optional[float] = None) -> List[List[compas.geometry.Polyline]]:
        pass
