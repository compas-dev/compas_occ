from typing import List, Tuple, Union, Optional

import compas.geometry
import compas.datastructures

from compas.geometry import Vector
from compas.geometry import Frame
from compas.geometry import Translation
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import Polygon
from compas.geometry import Plane
from compas.datastructures import Mesh
from compas.geometry import Brep

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Common
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeSolid
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Sewing
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Copy
from OCC.Core.BRepCheck import BRepCheck_Shell
from OCC.Core.BRepCheck import BRepCheck_Status
from OCC.Core.BRepExtrema import BRepExtrema_ShapeProximity
from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.BOPAlgo import BOPAlgo_Splitter
from OCC.Core.gp import gp_Pnt
from OCC.Core.GProp import GProp_GProps
from OCC.Core.ShapeFix import ShapeFix_Shell
from OCC.Core.TopAbs import TopAbs_VERTEX
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.TopAbs import TopAbs_WIRE
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopAbs import TopAbs_SHELL
from OCC.Core.TopAbs import TopAbs_SOLID
from OCC.Core.TopAbs import TopAbs_Orientation
from OCC.Core.TopAbs import TopAbs_ShapeEnum
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopExp import topexp_MapShapesAndUniqueAncestors
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import TopoDS_Iterator
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import topods
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
from OCC.Core.TopTools import TopTools_ListIteratorOfListOfShape  # type: ignore

from compas_occ.conversions import triangle_to_face
from compas_occ.conversions import quad_to_face
from compas_occ.conversions import ngon_to_face
from compas_occ.conversions import compas_transformation_to_trsf
from compas_occ.conversions import point_to_compas
from compas_occ.conversions import vector_to_occ
from compas_occ.conversions import location_to_compas
from compas_occ.conversions import frame_to_occ_ax2

# from compas_occ.geometry import OCCNurbsCurve
from compas_occ.geometry import OCCNurbsSurface

from .errors import BrepFilletError

from .brepvertex import OCCBrepVertex
from .brepedge import OCCBrepEdge
from .breploop import OCCBrepLoop
from .brepface import OCCBrepFace

# from .brepbuilder import OCCBrepBuilder


class OCCBrep(Brep):
    """
    Class for Boundary Representation of geometric entities.

    Attributes
    ----------
    vertices : list[:class:`~compas_occ.brep.OCCBrepVertex`], read-only
        The vertices of the Brep.
    edges : list[:class:`~compas_occ.brep.OCCBrepEdge`], read-only
        The edges of the Brep.
    loops : list[:class:`~compas_occ.brep.OCCBrepLoop`], read-only
        The loops of the Brep.
    faces : list[:class:`~compas_occ.brep.OCCBrepFace`], read-only
        The faces of the Brep.
    frame : :class:`~compas.geometry.Frame`, read-only
        The local coordinate system of the Brep.
    area : float, read-only
        The surface area of the Brep.
    volume : float, read-only
        The volume of the regions contained by the Brep.

    """

    _occ_shape: TopoDS_Shape

    def __init__(self) -> None:
        super().__init__()
        self._vertices = None
        self._edges = None
        self._loops = None
        self._faces = None
        self._shells = None
        self._solids = None

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self):
        return {
            "vertices": [v.data for v in self.vertices],
            "edges": [e.data for e in self.edges],
            "faces": [f.data for f in self.faces],
        }

    @classmethod
    def from_data(cls, data):
        """Construct an OCCBrep from its data representation.

        Parameters
        ----------
        data : :obj:`dict`
            The data dictionary.

        Returns
        -------
        :class:`~compas_occ.geometry.OCCBrep`

        """
        # brep = cls()
        # for vertexdata in data["vertices"]:
        #     builder.add_vertex(BrepVertexBuilder.from_data(vertexdata))
        # for edgedata in data["edges"]:
        #     pass
        #     # RhinoBrepEdge.from_data(e_data, builder)
        # for facedata in data["faces"]:
        #     pass
        #     # RhinoBrepFace.from_data(f_data, builder)
        # brep.native_brep = builder.result
        # return brep
        pass

    def copy(self, *args, **kwargs):
        """Deep-copy this BRep using the native OCC copying mechanism.

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        builder = BRepBuilderAPI_Copy(self.occ_shape)
        builder.Perform(self.occ_shape)
        return OCCBrep.from_native(builder.Shape())

    # ==============================================================================
    # Customization
    # ==============================================================================

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_shape(self) -> TopoDS_Shape:
        return self._occ_shape

    @occ_shape.setter
    def occ_shape(self, shape: TopoDS_Shape) -> None:
        self._occ_shape = shape
        self._vertices = None
        self._edges = None
        self._loops = None
        self._faces = None
        self._shells = None
        self._solids = None

    @property
    def native_brep(self) -> TopoDS_Shape:
        return self.occ_shape

    @native_brep.setter
    def native_brep(self, shape: TopoDS_Shape) -> None:
        self.occ_shape = shape

    @property
    def orientation(self) -> TopAbs_Orientation:
        return TopAbs_Orientation(self.occ_shape.Orientation())

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def type(self) -> TopAbs_ShapeEnum:
        return self.occ_shape.ShapeType()

    @property
    def is_shell(self):
        return self.type == TopAbs_ShapeEnum.TopAbs_SHELL

    @property
    def is_solid(self):
        return self.type == TopAbs_ShapeEnum.TopAbs_SOLID

    @property
    def is_compound(self):
        return self.type == TopAbs_ShapeEnum.TopAbs_COMPOUND

    @property
    def is_compoundsolid(self):
        return self.type == TopAbs_ShapeEnum.TopAbs_COMPSOLID

    @property
    def is_orientable(self) -> bool:
        return self.occ_shape.Orientable()

    @property
    def is_closed(self) -> bool:
        return self.occ_shape.Closed()

    @property
    def is_infinite(self) -> bool:
        return self.occ_shape.Infinite()

    @property
    def is_convex(self) -> bool:
        return self.occ_shape.Convex()

    @property
    def is_manifold(self) -> bool:
        return False

    @property
    def is_surface(self) -> bool:
        return False

    # ==============================================================================
    # Geometric Components
    # ==============================================================================

    @property
    def points(self) -> List[Point]:
        points = []
        for vertex in self.vertices:
            points.append(vertex.point)
        return points

    # @property
    # def curves(self) -> List[OCCNurbsCurve]:
    #     curves = []
    #     for edge in self.edges:
    #         curves.append(edge.nurbscurve)
    #     return curves

    # @property
    # def surfaces(self) -> List[OCCNurbsSurface]:
    #     surfaces = []
    #     for face in self.faces:
    #         surfaces.append(face.nurbssurface)
    #     return surfaces

    # ==============================================================================
    # Topological Components
    # ==============================================================================

    @property
    def vertices(self) -> List[OCCBrepVertex]:
        if self._vertices is None:
            vertices = []
            explorer = TopExp_Explorer(self.occ_shape, TopAbs_VERTEX)
            while explorer.More():
                vertex = explorer.Current()
                vertices.append(OCCBrepVertex(vertex))  # type: ignore
                explorer.Next()
            self._vertices = vertices
        return self._vertices

    @property
    def edges(self) -> List[OCCBrepEdge]:
        if self._edges is None:
            edges = []
            explorer = TopExp_Explorer(self.occ_shape, TopAbs_EDGE)
            while explorer.More():
                edge = explorer.Current()
                edges.append(OCCBrepEdge(edge))  # type: ignore
                explorer.Next()
            self._edges = edges
        return self._edges

    @property
    def loops(self) -> List[OCCBrepLoop]:
        if self._loops is None:
            loops = []
            explorer = TopExp_Explorer(self.occ_shape, TopAbs_WIRE)
            while explorer.More():
                wire = explorer.Current()
                loops.append(OCCBrepLoop(wire))  # type: ignore
                explorer.Next()
            self._loops = loops
        return self._loops

    @property
    def faces(self) -> List[OCCBrepFace]:
        if self._faces is None:
            faces = []
            explorer = TopExp_Explorer(self.occ_shape, TopAbs_FACE)
            while explorer.More():
                face = explorer.Current()
                faces.append(OCCBrepFace(face))  # type: ignore
                explorer.Next()
            self._faces = faces
        return self._faces

    @property
    def shells(self) -> List["OCCBrep"]:
        if self._shells is None:
            shells = []
            explorer = TopExp_Explorer(self.occ_shape, TopAbs_SHELL)
            while explorer.More():
                shell = explorer.Current()
                brep = Brep.from_native(shell)
                shells.append(brep)
                explorer.Next()
            self._shells = shells
        return self._shells

    @property
    def solids(self) -> List["OCCBrep"]:
        if self._solids is None:
            solids = []
            explorer = TopExp_Explorer(self.occ_shape, TopAbs_SOLID)
            while explorer.More():
                solid = explorer.Current()
                brep = Brep.from_native(solid)
                solids.append(brep)
                explorer.Next()
            self._solids = solids
        return self._solids

    # ==============================================================================
    # Geometric Properties
    # ==============================================================================

    @property
    def frame(self) -> Frame:
        location = self.occ_shape.Location()
        return location_to_compas(location)

    @property
    def area(self) -> float:
        props = GProp_GProps()
        brepgprop.SurfaceProperties(self.occ_shape, props)
        return props.Mass()

    @property
    def volume(self) -> float:
        props = GProp_GProps()
        brepgprop.VolumeProperties(self.occ_shape, props)
        return props.Mass()

    @property
    def centroid(self) -> Point:
        props = GProp_GProps()
        brepgprop.VolumeProperties(self.occ_shape, props)
        pnt = props.CentreOfMass()
        return point_to_compas(pnt)

    # ==============================================================================
    # Read/Write
    # ==============================================================================

    @classmethod
    def from_step(cls, filename: str) -> "OCCBrep":
        """
        Conctruct a BRep from the data contained in a STEP file.

        Parameters
        ----------
        filename : str

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        from OCC.Extend.DataExchange import read_step_file

        shape = read_step_file(filename)
        return cls.from_native(shape)  # type: ignore

    @classmethod
    def from_iges(cls, filename: str) -> "OCCBrep":
        """
        Conctruct a BRep from the data contained in a IGES file.

        Parameters
        ----------
        filename : str

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        from OCC.Extend.DataExchange import read_iges_file

        shape = read_iges_file(filename)
        return cls.from_native(shape)  # type: ignore

    def to_step(self, filepath: str, schema: str = "AP203", unit: str = "MM") -> None:
        """
        Write the BRep shape to a STEP file.

        Parameters
        ----------
        filepath : str
            Location of the file.
        schema : str, optional
            STEP file format schema.
        unit : str, optional
            Base units for the geometry in the file.

        Returns
        -------
        None

        """
        from OCC.Core.STEPControl import STEPControl_Writer
        from OCC.Core.STEPControl import STEPControl_AsIs
        from OCC.Core.IFSelect import IFSelect_RetDone
        from OCC.Core.Interface import Interface_Static

        step_writer = STEPControl_Writer()
        Interface_Static.SetCVal("write.step.unit", unit)
        step_writer.Transfer(self.occ_shape, STEPControl_AsIs)
        status = step_writer.Write(filepath)
        assert status == IFSelect_RetDone, status

    def to_stl(
        self,
        filepath: str,
        linear_deflection: float = 1e-3,
        angular_deflection: float = 0.5,
    ) -> bool:
        """
        Write the BRep shape to a STL file.

        Parameters
        ----------
        filepath : str
            Location of the file.
        linear_deflection : float, optional
            Allowable deviation between curved geometry and mesh discretisation.
        angular_deflection : float, optional
            Maximum angle between two adjacent facets.

        Returns
        -------
        None

        """
        from OCC.Core.StlAPI import StlAPI_Writer

        BRepMesh_IncrementalMesh(
            self.occ_shape,
            linear_deflection,
            theAngDeflection=angular_deflection,
        )

        stl_writer = StlAPI_Writer()
        stl_writer.SetASCIIMode(True)

        return stl_writer.Write(self.occ_shape, filepath)

    def to_iges(self, filepath: str) -> bool:
        """
        Write the BRep shape to a IGES file.

        Parameters
        ----------
        filepath : str
            Location of the file.

        Returns
        -------
        None

        """
        from OCC.Core.IGESControl import IGESControl_Writer

        iges_writer = IGESControl_Writer()
        if not iges_writer.AddShape(self.occ_shape):
            raise Exception("Failed to add shape to IGES writer.")

        iges_writer.ComputeModel()
        return iges_writer.Write(filepath)

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_shape(cls, shape: TopoDS_Shape) -> "OCCBrep":
        """
        Construct a BRep from an OCC shape.

        Parameters
        ----------
        shape : ``TopoDS_Shape``
            The OCC shape.

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        brep = cls()
        brep.native_brep = shape
        return brep

    @classmethod
    def from_native(cls, shape: TopoDS_Shape) -> "OCCBrep":
        """
        Construct a BRep from an OCC shape.

        Parameters
        ----------
        shape : ``TopoDS_Shape``
            The OCC shape.

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        return cls.from_shape(shape)

    @classmethod
    def from_polygons(cls, polygons: List[compas.geometry.Polygon]) -> "OCCBrep":
        """
        Construct a BRep from a set of polygons.

        Parameters
        ----------
        polygons : list[:class:`~compas.geometry.Polygon`]

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
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
        brep = cls.from_native(shell)
        brep.sew()
        brep.fix()
        return brep

    @classmethod
    def from_curves(cls, curves: List[compas.geometry.NurbsCurve]) -> "OCCBrep":
        """
        Construct a BRep from a set of curves.

        Parameters
        ----------
        curves : list[:class:`~compas.geometry.NurbsCurve`]

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        raise NotImplementedError

    @classmethod
    def from_box(cls, box: compas.geometry.Box) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS box.

        Parameters
        ----------
        box : :class:`~compas.geometry.Box`

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        xaxis = box.frame.xaxis.scaled(-0.5 * box.xsize)
        yaxis = box.frame.yaxis.scaled(-0.5 * box.ysize)
        zaxis = box.frame.zaxis.scaled(-0.5 * box.zsize)
        frame = box.frame.transformed(Translation.from_vector(xaxis + yaxis + zaxis))
        ax2 = frame_to_occ_ax2(frame)  # type: ignore
        shape = BRepPrimAPI_MakeBox(ax2, box.xsize, box.ysize, box.zsize).Shape()
        return cls.from_native(shape)

    @classmethod
    def from_sphere(cls, sphere: compas.geometry.Sphere) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS sphere.

        Parameters
        ----------
        sphere : :class:`~compas.geometry.Sphere`

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        shape = BRepPrimAPI_MakeSphere(
            gp_Pnt(*sphere.frame.point), sphere.radius
        ).Shape()
        return cls.from_native(shape)

    @classmethod
    def from_cylinder(cls, cylinder: compas.geometry.Cylinder) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS cylinder.

        Parameters
        ----------
        cylinder : :class:`~compas.geometry.Cylinder`

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        height = cylinder.height
        radius = cylinder.radius
        frame = cylinder.frame
        frame.transform(Translation.from_vector(frame.zaxis * (-0.5 * height)))
        ax2 = frame_to_occ_ax2(frame)
        shape = BRepPrimAPI_MakeCylinder(ax2, radius, height).Shape()
        return cls.from_native(shape)

    @classmethod
    def from_cone(cls, cone: compas.geometry.Cone) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS cone.

        Parameters
        ----------
        cone : :class:`~compas.geometry.Cone`

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        raise NotImplementedError

    @classmethod
    def from_torus(cls, torus: compas.geometry.Torus) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS torus.

        Parameters
        ----------
        torus : :class:`~compas.geometry.Torus`

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        raise NotImplementedError

    @classmethod
    def from_mesh(
        cls, mesh: compas.datastructures.Mesh, solid: bool = True
    ) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS mesh.

        Parameters
        ----------
        mesh : :class:`~compas.datastructures.Mesh`

        Returns
        -------
        :class:`OCCBrep`

        """
        shell = TopoDS_Shell()
        builder = BRep_Builder()
        builder.MakeShell(shell)
        for face in mesh.faces():
            points = mesh.face_polygon(face)
            if len(points) == 3:
                builder.Add(shell, triangle_to_face(points))
            elif len(points) == 4:
                builder.Add(shell, quad_to_face(points))
            else:
                builder.Add(shell, ngon_to_face(points))
        brep = cls.from_native(shell)
        brep.sew()
        brep.fix()
        if solid:
            brep.make_solid()
        return brep

    @classmethod
    def from_brepfaces(cls, faces: List[OCCBrepFace]) -> "OCCBrep":
        """
        Make a BRep from a list of BRep faces forming an open or closed shell.

        Parameters
        ----------
        faces : list[:class:`OCCBrepFace`]

        Returns
        -------
        :class:`OCCBrep`

        """
        shell = TopoDS_Shell()
        builder = BRep_Builder()
        builder.MakeShell(shell)
        for face in faces:
            if not face.is_valid():
                face.fix()
            builder.Add(shell, face.occ_face)
        brep = cls.from_native(shell)
        brep.sew()
        brep.fix()
        return brep

    @classmethod
    def from_planes(cls, planes: list[Plane]) -> "OCCBrep":
        """
        Make a BRep from a list of planes.

        Parameters
        ----------
        planes : list[:class:`compas.geometry.Plane`]

        Returns
        -------
        :class:`OCCBrep`

        """
        faces = []
        for plane in planes:
            faces.append(OCCBrepFace.from_plane(plane))
        return cls.from_brepfaces(faces)

    @classmethod
    def from_extrusion(
        cls,
        profile: Union[OCCBrepEdge, OCCBrepFace],
        vector: Vector,
    ) -> "OCCBrep":
        """
        Construct a BRep by extruding a closed curve along a direction vector.

        References
        ----------
        https://dev.opencascade.org/doc/occt-7.4.0/refman/html/class_b_rep_prim_a_p_i___make_prism.html

        """
        brep = cls()
        brep.native_brep = BRepPrimAPI_MakePrism(
            profile.occ_shape,
            vector_to_occ(vector),
        ).Shape()
        return brep

    @classmethod
    def from_sweep(
        cls,
        profile: Union[OCCBrepEdge, OCCBrepFace],
        path: OCCBrepLoop,
    ) -> "OCCBrep":
        """
        Construct a BRep by sweeping a profile along a path.

        References
        ----------
        https://dev.opencascade.org/doc/occt-7.4.0/refman/html/class_b_rep_prim_a_p_i___make_sweep.html
        https://dev.opencascade.org/doc/occt-7.4.0/refman/html/class_b_rep_offset_a_p_i___make_pipe.html
        https://dev.opencascade.org/doc/occt-7.4.0/refman/html/class_b_rep_offset_a_p_i___make_pipe_shell.html

        """
        brep = cls()
        brep.native_brep = BRepOffsetAPI_MakePipe(
            path.occ_wire,
            profile.occ_shape,
        ).Shape()
        return brep

    # create patch
    # create offset

    @classmethod
    def from_breps(cls, breps: List["OCCBrep"]) -> "OCCBrep":
        """
        Construct one compound BRep out of multiple individual BReps.
        """
        compound = TopoDS_Compound()
        builder = BRep_Builder()
        builder.MakeCompound(compound)
        for brep in breps:
            builder.Add(compound, brep.native_brep)
        return cls.from_native(compound)

    @classmethod
    def from_surface(
        cls,
        surface: Union[compas.geometry.Surface, OCCNurbsSurface],
        domain_u: Optional[Tuple[float, float]] = None,
        domain_v: Optional[Tuple[float, float]] = None,
        precision: float = 1e-6,
        loop: Optional[OCCBrepLoop] = None,
        inside: bool = True,
    ) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS surface.

        Parameters
        ----------
        surface : :class:`~compas.geometry.Surface`
        domain_u : tuple, optional
            The domain of the surface in the U direction.
        domain_v : tuple, optional
            The domain of the surface in the V direction.
        precision : float, optional
            The precision of the discretisation of the surface.
        loop : :class:`OCCBrepLoop`, optional
            The loop to trim the surface with.
        inside : bool, optional
            Whether to keep the inside or outside of the loop.

        Returns
        -------
        :class:`OCCBrep`

        """
        face = OCCBrepFace.from_surface(
            surface,  # type: ignore
            domain_u=domain_u,
            domain_v=domain_v,
            precision=precision,
            loop=loop,
            inside=inside,
        )
        return cls.from_brepfaces([face])

    # ==============================================================================
    # Boolean Constructors
    # ==============================================================================

    @classmethod
    def from_boolean_difference(cls, A: "OCCBrep", B: "OCCBrep") -> "OCCBrep":
        """
        Construct a BRep from the boolean difference of two other BReps.

        Parameters
        ----------
        A : :class:`~compas_occ.brep.OCCBrep`
        B : :class:`~compas_occ.brep.OCCBrep`

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        cut = BRepAlgoAPI_Cut(A.native_brep, B.native_brep)
        if not cut.IsDone():
            raise Exception("Boolean difference operation could not be completed.")
        brep = cls.from_native(cut.Shape())
        brep.sew()
        brep.fix()
        brep.make_solid()
        return brep

    @classmethod
    def from_boolean_intersection(cls, A: "OCCBrep", B: "OCCBrep") -> "OCCBrep":
        """
        Construct a BRep from the boolean intersection of two other BReps.

        Parameters
        ----------
        A : :class:`~compas_occ.brep.OCCBrep`
        B : :class:`~compas_occ.brep.OCCBrep`

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        common = BRepAlgoAPI_Common(A.native_brep, B.native_brep)
        if not common.IsDone():
            raise Exception("Boolean intersection operation could not be completed.")
        brep = cls.from_native(common.Shape())
        brep.sew()
        brep.fix()
        brep.make_solid()
        return brep

    @classmethod
    def from_boolean_union(cls, A: "OCCBrep", B: "OCCBrep") -> "OCCBrep":
        """
        Construct a BRep from the boolean union of two other BReps.

        Parameters
        ----------
        A : :class:`~compas_occ.brep.OCCBrep`
        B : :class:`~compas_occ.brep.OCCBrep`

        Returns
        -------
        :class:`~compas_occ.brep.OCCBrep`

        """
        fuse = BRepAlgoAPI_Fuse(A.native_brep, B.native_brep)
        if not fuse.IsDone():
            raise Exception("Boolean union operation could not be completed.")
        brep = cls.from_native(fuse.Shape())
        brep.sew()
        brep.fix()
        brep.make_solid()
        return brep

    # ==============================================================================
    # Converters
    # ==============================================================================

    def to_tesselation(
        self, linear_deflection: float = 1
    ) -> tuple[Mesh, list[Polyline]]:
        """
        Create a tesselation of the shape for visualisation.

        Parameters
        ----------
        linear_deflection : float, optional
            Allowable deviation between curved geometry and mesh discretisation.

        Returns
        -------
        tuple[:class:`~compas.datastructures.Mesh`, list[:class:`~compas.geometry.Polyline`]]

        """
        BRepMesh_IncrementalMesh(self.occ_shape, linear_deflection)
        bt = BRep_Tool()
        mesh = Mesh()
        polylines = []
        seen = []
        for face in self.faces:
            location = TopLoc_Location()
            triangulation = bt.Triangulation(face.occ_face, location)
            if triangulation is None:
                continue
            nodes = []
            trsf = location.Transformation()
            for i in range(1, triangulation.NbNodes() + 1):
                nodes.append(triangulation.Node(i).Transformed(trsf))
            vertices = [point_to_compas(node) for node in nodes]
            faces = []
            triangles = triangulation.Triangles()
            for i in range(1, triangulation.NbTriangles() + 1):
                triangle = triangles.Value(i)
                u, v, w = triangle.Get()
                faces.append([u - 1, v - 1, w - 1])
            # this can be done much more efficiently
            other = Mesh.from_vertices_and_faces(vertices, faces)
            mesh.join(other)
            # process the face loops to produce edges with the same discretisation as the faces
            for loop in face.loops:
                for edge in loop.edges:
                    if any(edge.is_same(e) for e in seen):
                        continue
                    seen.append(edge)
                    pot = bt.PolygonOnTriangulation(
                        edge.occ_edge, triangulation, location
                    )
                    if pot is None:
                        continue
                    points = []
                    nodes = pot.Nodes()
                    for i in range(1, pot.NbNodes() + 1):
                        node = nodes.Value(i)
                        points.append(vertices[node - 1])
                    polylines.append(Polyline(points))
        return mesh, polylines

    def to_meshes(self, u=16, v=16):
        """
        Convert the faces of the BRep shape to meshes.

        Parameters
        ----------
        u : int, optional
            The number of mesh faces in the U direction of the underlying surface geometry of every face of the Brep.
        v : int, optional
            The number of mesh faces in the V direction of the underlying surface geometry of every face of the Brep.

        Returns
        -------
        list[:class:`~compas.datastructures.Mesh`]

        """
        converter = BRepBuilderAPI_NurbsConvert(self.occ_shape, False)
        brep = OCCBrep.from_shape(converter.Shape())
        meshes = []
        for face in brep.faces:
            srf = OCCNurbsSurface.from_face(face.occ_face)
            mesh = srf.to_tesselation()
            meshes.append(mesh)
        return meshes

    def to_polygons(self):
        """
        Convert the faces of the BRep to simple polygons without underlying geometry."""
        polygons = []
        for face in self.faces:
            points = []
            for vertex in face.loops[0].vertices:
                points.append(vertex.point)
            polygons.append(Polygon(points))
        return polygons

    def to_viewmesh(self, linear_deflection=0.001):
        """
        Convert the BRep to a view mesh."""
        return self.to_tesselation(linear_deflection=linear_deflection)

    # ==============================================================================
    # Relationships
    # ==============================================================================

    def vertex_neighbors(self, vertex: OCCBrepVertex) -> List[OCCBrepVertex]:
        """
        Identify the neighbouring vertices of a given vertex.

        Parameters
        ----------
        vertex : :class:`OCCBrepVertex`

        Returns
        -------
        List[:class:`OCCBrepVertex`]

        """
        map = TopTools_IndexedDataMapOfShapeListOfShape()
        topexp_MapShapesAndUniqueAncestors(
            self.occ_shape, TopAbs_VERTEX, TopAbs_EDGE, map
        )
        results = map.FindFromKey(vertex.occ_vertex)
        iterator = TopTools_ListIteratorOfListOfShape(results)
        vertices = []
        while iterator.More():
            edge = topods.Edge(iterator.Value())
            edge = OCCBrepEdge(edge)
            iterator.Next()
            if not edge.first_vertex.occ_vertex.IsSame(vertex.occ_vertex):
                vertices.append(edge.first_vertex)
            else:
                vertices.append(edge.last_vertex)
        return vertices

    def vertex_edges(self, vertex: OCCBrepVertex) -> List[OCCBrepEdge]:
        """
        Identify the edges connected to a given vertex.

        Parameters
        ----------
        vertex : :class:`OCCBrepVertex`

        Returns
        -------
        List[:class:`OCCBrepEdge`]

        """
        map = TopTools_IndexedDataMapOfShapeListOfShape()
        topexp_MapShapesAndUniqueAncestors(
            self.occ_shape, TopAbs_VERTEX, TopAbs_EDGE, map
        )
        results = map.FindFromKey(vertex.occ_vertex)
        iterator = TopTools_ListIteratorOfListOfShape(results)
        edges = []
        while iterator.More():
            edge = iterator.Value()
            edges.append(OCCBrepEdge(edge))
            iterator.Next()
        return edges

    def vertex_faces(self, vertex: OCCBrepVertex) -> List[OCCBrepFace]:
        """
        Identify the faces connected to a vertex.

        Parameters
        ----------
        vertex : :class:`OCCBrepVertex`

        Returns
        -------
        List[:class:`OCCBrepFace`]

        """
        map = TopTools_IndexedDataMapOfShapeListOfShape()
        topexp_MapShapesAndUniqueAncestors(
            self.occ_shape, TopAbs_VERTEX, TopAbs_FACE, map
        )
        results = map.FindFromKey(vertex.occ_vertex)
        iterator = TopTools_ListIteratorOfListOfShape(results)
        faces = []
        while iterator.More():
            face = iterator.Value()
            faces.append(OCCBrepFace(face))
            iterator.Next()
        return faces

    def edge_faces(self, edge: OCCBrepEdge) -> List[OCCBrepFace]:
        """
        Identify the faces connected to an edge.

        Parameters
        ----------
        edge : :class:`OCCBrepEdge`

        Returns
        -------
        List[:class:`OCCBrepFace`]

        """
        map = TopTools_IndexedDataMapOfShapeListOfShape()
        topexp_MapShapesAndUniqueAncestors(
            self.occ_shape, TopAbs_EDGE, TopAbs_FACE, map
        )
        results = map.FindFromKey(edge.occ_edge)
        iterator = TopTools_ListIteratorOfListOfShape(results)
        faces = []
        while iterator.More():
            face = iterator.Value()
            faces.append(OCCBrepFace(face))
            iterator.Next()
        return faces

    def edge_loops(self, edge: OCCBrepEdge) -> List[OCCBrepLoop]:
        """Identify the parent loops of an edge.

        Parameters
        ----------
        edge : :class:`OCCBrepEdge`
            The edge.

        Returns
        -------
        List[:class:`OCCBrepLoop`]
            The loops.

        """

        map = TopTools_IndexedDataMapOfShapeListOfShape()
        topexp_MapShapesAndUniqueAncestors(
            self.occ_shape, TopAbs_EDGE, TopAbs_WIRE, map
        )
        results = map.FindFromKey(edge.occ_edge)
        iterator = TopTools_ListIteratorOfListOfShape(results)
        loops = []
        while iterator.More():
            wire = iterator.Value()
            loops.append(OCCBrepLoop(wire))
            iterator.Next()
        return loops

    # ==============================================================================
    # Other Methods
    # ==============================================================================

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
    # trim
    # rotate
    # translate
    # unjoin edges

    def make_solid(self):
        """
        Convert the current shape to a solid if it is a shell.

        Returns
        -------
        None

        """
        if self.type == TopAbs_ShapeEnum.TopAbs_SHELL:
            self.occ_shape = BRepBuilderAPI_MakeSolid(self.occ_shape).Shape()  # type: ignore

    def check(self):
        """
        Check the shape.

        Returns
        -------
        None

        """
        if self.type == TopAbs_ShapeEnum.TopAbs_SHELL:
            check = BRepCheck_Shell(self.occ_shape)  # type: ignore
            print(BRepCheck_Status(check.Closed()))
            print(BRepCheck_Status(check.Orientation()))

    def sew(self):
        """
        Sew together the individual parts of the shape.

        Returns
        -------
        None

        """
        if len(self.faces) > 1:
            sewer = BRepBuilderAPI_Sewing()
            sewer.Load(self.occ_shape)
            sewer.Perform()
            self.occ_shape = sewer.SewedShape()

    def fix(self):
        """
        Fix the shell.

        Returns
        -------
        None

        """
        if self.type == TopAbs_ShapeEnum.TopAbs_SHELL:
            fixer = ShapeFix_Shell(self.occ_shape)  # type: ignore
            fixer.Perform()
            self.occ_shape = fixer.Shell()

    def heal(self):
        """
        Heal the shape.

        Returns
        -------
        None

        """
        self.sew()
        self.fix()

    def cull_unused_vertices(self) -> None:
        """
        Remove all unused vertices.

        Returns
        -------
        None

        """
        pass

    def cull_unused_edges(self) -> None:
        """
        Remove all unused edges.

        Returns
        -------
        None

        """
        pass

    def cull_unused_loops(self) -> None:
        """
        Remove all unused loops.

        Returns
        -------
        None

        """
        pass

    def cull_unused_faces(self) -> None:
        """
        Remove all unused faces.

        Returns
        -------
        None

        """
        pass

    def transform(self, matrix: compas.geometry.Transformation) -> None:
        """
        Transform this Brep.

        Parameters
        ----------
        matrix : :class:`compas.geometry.Transformation`
            A transformation matrix.

        Returns
        -------
        None

        """
        trsf = compas_transformation_to_trsf(matrix)
        builder = BRepBuilderAPI_Transform(self.occ_shape, trsf, True)
        shape = builder.ModifiedShape(self.occ_shape)
        self._occ_shape = shape

    def transformed(self, matrix: compas.geometry.Transformation) -> "OCCBrep":
        """
        Return a transformed copy of the Brep.

        Parameters
        ----------
        matrix : :class:`compas.geometry.Transformation`
            A transformation matrix.

        Returns
        -------
        :class:`OCCBrep`

        """
        trsf = compas_transformation_to_trsf(matrix)
        builder = BRepBuilderAPI_Transform(self.occ_shape, trsf, True)
        shape = builder.ModifiedShape(self.occ_shape)
        return OCCBrep.from_shape(shape)

    def contours(
        self, planes: List[compas.geometry.Plane]
    ) -> List[List[compas.geometry.Polyline]]:
        """
        Generate contour lines by slicing the BRep shape with a series of planes.

        Parameters
        ----------
        planes : list[:class:`~compas.geometry.Plane`]
            The slicing planes.

        Returns
        -------
        list[list[:class:`~compas.geometry.Polyline`]]
            A list of polylines per plane.

        """
        raise NotImplementedError

    def overlap(
        self,
        other: "OCCBrep",
        deflection: float = 1e-3,
        tolerance: float = 0.0,
    ) -> Tuple[List[OCCBrepFace], List[OCCBrepFace]]:
        """
        Compute the overlap between this BRep and another.

        Parameters
        ----------
        other : :class:`OCCBrep`
            The other b-rep.
        deflection : float, optional
            Allowable deflection for mesh generation used for proximity detection.
        tolerance : float, optional
            Tolerance for overlap calculation.

        Returns
        -------
        Tuple[List[:class:`OCCBrepFace`], List[:class:`OCCBrepFace`]]

        """
        mesher1 = BRepMesh_IncrementalMesh(self.occ_shape, deflection)
        mesher2 = BRepMesh_IncrementalMesh(other.native_brep, deflection)
        mesher1.Perform()
        mesher2.Perform()
        proximity = BRepExtrema_ShapeProximity(
            self.occ_shape,
            other.native_brep,
            tolerance,
        )
        proximity.Perform()

        overlaps1 = proximity.OverlapSubShapes1()
        keys1 = overlaps1.Keys()
        faces1 = []
        for key in keys1:
            face = proximity.GetSubShape1(key)
            faces1.append(OCCBrepFace(face))

        overlaps2 = proximity.OverlapSubShapes2()
        keys2 = overlaps2.Keys()
        faces2 = []
        for key in keys2:
            face = proximity.GetSubShape2(key)
            faces2.append(OCCBrepFace(face))

        return faces1, faces2

    def slice(self, plane: compas.geometry.Plane) -> Union["OCCBrep", None]:
        """Slice a BRep with a plane.

        Parameters
        ----------
        plane : :class:`~compas.geometry.Plane`
            The slicing plane.

        Returns
        -------
        :class:`OCCBrepFace` | None
            The resulting Brep slice or None if the plane does not intersect the Brep.

        """
        if isinstance(plane, Frame):
            plane = Plane.from_frame(plane)

        face = OCCBrepFace.from_plane(plane)
        section = BRepAlgoAPI_Section(self.occ_shape, face.occ_face)
        section.Build()
        if section.IsDone():
            occ_shape = section.Shape()
            return OCCBrep.from_native(occ_shape)

    def trim(self, plane: compas.geometry.Plane) -> None:
        """Trim a Brep with a plane.

        Parameters
        ----------
        plane : :class:`~compas.geometry.Plane`
            The slicing plane.

        Returns
        -------
        None

        """
        from compas_occ.occ import split_shapes
        from compas_occ.occ import compute_shape_centreofmass
        from compas.geometry import is_point_infront_plane

        if isinstance(plane, Frame):
            plane = Plane.from_frame(plane)

        arguments = [self.occ_shape]
        tools = [OCCBrepFace.from_plane(plane).occ_shape]
        results = split_shapes(arguments, tools)  # type: ignore

        occ_shape = None
        for test in results:
            point = compute_shape_centreofmass(test)
            if is_point_infront_plane(point, plane):
                occ_shape = test
                break
        if occ_shape:
            self.occ_shape = occ_shape

    def trimmed(self, plane: compas.geometry.Plane) -> "OCCBrep":
        """Construct a copy of a Brep trimmed with a plane.

        Parameters
        ----------
        plane : :class:`~compas.geometry.Plane`
            The slicing plane.

        Returns
        -------
        :class:`OCCBrep`

        """
        brep = self.copy()
        brep.trim(plane)
        return brep

    def split(self, other: "OCCBrep") -> List["OCCBrep"]:
        """Split a BRep using another BRep as splitter.

        Parameters
        ----------
        other : :class:`OCCBrep`
            Another b-rep.

        Returns
        -------
        List[:class:`~compas_occ.brep.OCCBrep`]

        """
        splitter = BOPAlgo_Splitter()
        splitter.AddArgument(self.occ_shape)
        splitter.AddTool(other.occ_shape)
        splitter.Perform()
        shape = splitter.Shape()
        results = []
        if isinstance(shape, TopoDS_Compound):
            it = TopoDS_Iterator(shape)
            while it.More():
                results.append(it.Value())
                it.Next()
        else:
            results.append(shape)
        return [OCCBrep.from_shape(result) for result in results]

    def fillet(
        self,
        radius: float,
        exclude: Optional[list[OCCBrepEdge]] = None,
    ) -> None:
        """Fillet the edges of a BRep.

        Parameters
        ----------
        radius : float
            The radius of the fillet.
        exclude : list[:class:`OCCBrepEdge`], optional
            A list of edges to exclude from the fillet operation.

        Raises
        ------
        BrepFilletError
            If the fillet operation could not be completed.

        Returns
        -------
        None
            the Brep is modified in-place.

        """
        fillet = BRepFilletAPI_MakeFillet(self.occ_shape)
        for edge in self.edges:
            if exclude:
                if any(e.is_same(edge) for e in exclude):
                    continue
            fillet.Add(radius, edge.occ_edge)
        fillet.Build()
        if fillet.IsDone():
            self.occ_shape = fillet.Shape()
        else:
            raise BrepFilletError("Fillet operation could not be completed.")

    def filleted(
        self, radius: float, exclude: Optional[list[OCCBrepEdge]] = None
    ) -> "OCCBrep":
        """Construct a copy of a Brep with filleted edges.

        Parameters
        ----------
        radius : float
            The radius of the fillet.
        exclude : list[:class:`OCCBrepEdge`], optional
            A list of edges to exclude from the fillet operation.

        Returns
        -------
        :class:`OCCBrep`

        """
        brep = self.copy()
        brep.fillet(radius, exclude=exclude)
        return brep
