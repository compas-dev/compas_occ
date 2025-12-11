import pathlib
from typing import Optional
from typing import Union

from OCC.Core import APIHeaderSection
from OCC.Core import Bnd
from OCC.Core import BOPAlgo
from OCC.Core import BRep
from OCC.Core import BRepAlgoAPI
from OCC.Core import BRepBndLib
from OCC.Core import BRepBuilderAPI
from OCC.Core import BRepCheck
from OCC.Core import BRepExtrema
from OCC.Core import BRepFilletAPI
from OCC.Core import BRepGProp
from OCC.Core import BRepMesh
from OCC.Core import BRepOffsetAPI
from OCC.Core import BRepPrimAPI
from OCC.Core import BRepTools
from OCC.Core import GProp
from OCC.Core import IFSelect
from OCC.Core import IGESControl
from OCC.Core import Interface
from OCC.Core import ShapeFix
from OCC.Core import ShapeUpgrade
from OCC.Core import STEPControl
from OCC.Core import StlAPI
from OCC.Core import TCollection
from OCC.Core import TopAbs
from OCC.Core import TopExp
from OCC.Core import TopLoc
from OCC.Core import TopoDS
from OCC.Core import TopTools
from OCC.Core import gp
from OCC.Extend import DataExchange

import compas.datastructures
import compas.geometry
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Brep
from compas.geometry import Frame
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Polygon
from compas.geometry import Polyline
from compas.geometry import Translation
from compas.geometry import Vector
from compas.geometry import is_point_behind_plane
from compas.tolerance import TOL
from compas_occ.conversions import aabb_to_compas
from compas_occ.conversions import compas_transformation_to_trsf
from compas_occ.conversions import frame_to_occ_ax2
from compas_occ.conversions import location_to_compas
from compas_occ.conversions import ngon_to_face
from compas_occ.conversions import obb_to_compas
from compas_occ.conversions import point_to_compas
from compas_occ.conversions import quad_to_face
from compas_occ.conversions import triangle_to_face
from compas_occ.conversions import vector_to_occ
from compas_occ.geometry import OCCCurve
from compas_occ.geometry import OCCNurbsSurface
from compas_occ.geometry import OCCSurface
from compas_occ.occ import compute_shape_centreofmass
from compas_occ.occ import split_shapes

from .brepedge import OCCBrepEdge
from .brepface import OCCBrepFace
from .breploop import OCCBrepLoop
from .brepvertex import OCCBrepVertex
from .errors import BrepBooleanError
from .errors import BrepFilletError


class OCCBrep(Brep):
    """
    Class for Boundary Representation of geometric entities.

    Attributes
    ----------
    vertices
        The vertices of the Brep.
    edges
        The edges of the Brep.
    loops
        The loops of the Brep.
    faces
        The faces of the Brep.
    frame
        The local coordinate system of the Brep.
    area
        The surface area of the Brep.
    volume
        The volume of the regions contained by the Brep.

    """

    _occ_shape: TopoDS.TopoDS_Shape

    @property
    def __data__(self) -> dict:
        return {
            "vertices": [vertex.__data__ for vertex in self.vertices],
            "edges": [edge.__data__ for edge in self.edges],
            "faces": [face.__data__ for face in self.faces],
        }

    @classmethod
    def __from_data__(cls, data: dict) -> "OCCBrep":
        """Construct an OCCBrep from its data representation.

        Parameters
        ----------
        data
            The data dictionary.

        Returns
        -------
        OCCBrep

        """
        from .builder import OCCBrepBuilder

        builder = OCCBrepBuilder()
        brep = builder.build(data["faces"])
        return brep

    def __init__(self) -> None:
        super().__init__()
        self._vertices = None
        self._edges = None
        self._loops = None
        self._faces = None
        self._shells = None
        self._solids = None

        self._aabb = None
        self._obb = None
        self._area = None
        self._volume = None
        self._centroid = None

    def copy(self) -> "OCCBrep":
        """Deep-copy this BRep using the native OCC copying mechanism.

        Returns
        -------
        OCCBrep

        """
        builder = BRepBuilderAPI.BRepBuilderAPI_Copy(self.occ_shape)
        builder.Perform(self.occ_shape)
        return OCCBrep.from_native(builder.Shape())

    # ==============================================================================
    # Customization
    # ==============================================================================

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_shape(self) -> TopoDS.TopoDS_Shape:
        return self._occ_shape

    @occ_shape.setter
    def occ_shape(self, shape: TopoDS.TopoDS_Shape) -> None:
        self._occ_shape = shape
        self._vertices = None
        self._edges = None
        self._loops = None
        self._faces = None
        self._shells = None
        self._solids = None

    @property
    def native_brep(self) -> TopoDS.TopoDS_Shape:
        return self.occ_shape

    @native_brep.setter
    def native_brep(self, shape: TopoDS.TopoDS_Shape) -> None:
        self.occ_shape = shape

    @property
    def orientation(self) -> TopAbs.TopAbs_Orientation:
        return TopAbs.TopAbs_Orientation(self.occ_shape.Orientation())

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def type(self) -> TopAbs.TopAbs_ShapeEnum:
        return self.occ_shape.ShapeType()

    @property
    def is_shell(self):
        return self.type == TopAbs.TopAbs_SHELL

    @property
    def is_solid(self):
        return self.type == TopAbs.TopAbs_SOLID

    @property
    def is_compound(self):
        return self.type == TopAbs.TopAbs_COMPOUND

    @property
    def is_compoundsolid(self):
        return self.type == TopAbs.TopAbs_COMPSOLID

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
    def points(self) -> list[Point]:
        points = []
        seen = []
        for vertex in self.vertices:
            if any(vertex.is_same(test) for test in seen):
                continue
            seen.append(vertex)
            points.append(vertex.point)
        return points

    @property
    def curves(self) -> list[OCCCurve]:
        curves = []
        for edge in self.edges:
            curves.append(edge.curve)
        return curves

    @property
    def surfaces(self) -> list[OCCSurface]:
        surfaces = []
        for face in self.faces:
            surfaces.append(face.surface)
        return surfaces

    # ==============================================================================
    # Topological Components
    # ==============================================================================

    @property
    def vertices(self) -> list[OCCBrepVertex]:
        # this will return ALL topological vertices of the shape
        # that means, the vertices, the vertices of the edges, the vertices of the faces, ...
        # many of those vertices are duplicates
        if self._vertices is None:
            vertices = []
            explorer = TopExp.TopExp_Explorer(self.occ_shape, TopAbs.TopAbs_VERTEX)  # type: ignore
            while explorer.More():
                vertex = explorer.Current()
                vertices.append(OCCBrepVertex(vertex))  # type: ignore
                explorer.Next()
            self._vertices = vertices
        return self._vertices

    @property
    def edges(self) -> list[OCCBrepEdge]:
        if self._edges is None:
            edges = []
            explorer = TopExp.TopExp_Explorer(self.occ_shape, TopAbs.TopAbs_EDGE)  # type: ignore
            while explorer.More():
                edge = explorer.Current()
                edges.append(OCCBrepEdge(edge))  # type: ignore
                explorer.Next()
            self._edges = edges
        return self._edges

    @property
    def loops(self) -> list[OCCBrepLoop]:
        if self._loops is None:
            loops = []
            explorer = TopExp.TopExp_Explorer(self.occ_shape, TopAbs.TopAbs_WIRE)  # type: ignore
            while explorer.More():
                wire = explorer.Current()
                loops.append(OCCBrepLoop(wire))  # type: ignore
                explorer.Next()
            self._loops = loops
        return self._loops

    @property
    def faces(self) -> list[OCCBrepFace]:
        if self._faces is None:
            faces = []
            explorer = TopExp.TopExp_Explorer(self.occ_shape, TopAbs.TopAbs_FACE)  # type: ignore
            while explorer.More():
                face = explorer.Current()
                faces.append(OCCBrepFace(face))  # type: ignore
                explorer.Next()
            self._faces = faces
        return self._faces

    @property
    def shells(self) -> list["OCCBrep"]:
        if self._shells is None:
            shells = []
            explorer = TopExp.TopExp_Explorer(self.occ_shape, TopAbs.TopAbs_SHELL)  # type: ignore
            while explorer.More():
                shell = explorer.Current()
                brep: OCCBrep = OCCBrep.from_native(shell)
                shells.append(brep)
                explorer.Next()
            self._shells = shells
        return self._shells

    @property
    def solids(self) -> list["OCCBrep"]:
        if self._solids is None:
            solids = []
            explorer = TopExp.TopExp_Explorer(self.occ_shape, TopAbs.TopAbs_SOLID)  # type: ignore
            while explorer.More():
                solid = explorer.Current()
                brep: OCCBrep = OCCBrep.from_native(solid)
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
        # if self._area is None:
        props = GProp.GProp_GProps()
        BRepGProp.brepgprop.SurfaceProperties(self.native_brep, props)
        self._area = props.Mass()
        return self._area

    @property
    def volume(self) -> float:
        # if self._volume is None:
        props = GProp.GProp_GProps()
        BRepGProp.brepgprop.VolumeProperties(self.occ_shape, props)
        self._volume = props.Mass()
        return self._volume

    @property
    def centroid(self) -> Point:
        # if self._centroid is None:
        props = GProp.GProp_GProps()
        BRepGProp.brepgprop.VolumeProperties(self.occ_shape, props)
        pnt = props.CentreOfMass()
        self._centroid = point_to_compas(pnt)
        return self._centroid

    @property
    def aabb(self) -> Box:
        aabb = Bnd.Bnd_Box()
        BRepBndLib.brepbndlib.Add(self.native_brep, aabb, True)
        return aabb_to_compas(aabb)

    @property
    def obb(self) -> Box:
        obb = Bnd.Bnd_OBB()
        BRepBndLib.brepbndlib.AddOBB(self.native_brep, obb, True, True, True)
        return obb_to_compas(obb)

    @property
    def convex_hull(self) -> Mesh:
        raise NotImplementedError

    # ==============================================================================
    # Read/Write
    # ==============================================================================

    @classmethod
    def from_step(
        cls,
        filename: Union[str, pathlib.Path],
        heal: bool = False,
        solid: bool = False,
    ) -> "OCCBrep":
        """
        Conctruct a BRep from the data contained in a STEP file.

        Parameters
        ----------
        filename
            The file.
        solid
            If True, convert shells to solids when possible.

        Returns
        -------
        OCCBrep

        """
        shape = DataExchange.read_step_file(str(filename), verbosity=False)
        brep = cls.from_native(shape)  # type: ignore
        if heal:
            brep.heal()
        if solid:
            brep.make_solid()
        return brep

    @classmethod
    def from_iges(cls, filename: Union[str, pathlib.Path], solid: bool = True) -> "OCCBrep":
        """
        Conctruct a BRep from the data contained in a IGES file.

        Parameters
        ----------
        filename
            The file.
        solid
            If True, convert shells to solids when possible.

        Returns
        -------
        OCCBrep

        """
        shape = DataExchange.read_iges_file(str(filename))
        brep = cls.from_native(shape)  # type: ignore
        brep.heal()
        if solid:
            brep.make_solid()
        return brep

    def to_brep(
        self,
        filepath: Union[str, pathlib.Path],
    ) -> None:
        """
        Write the BRep shape to a BREP file.

        Parameters
        ----------
        filepath
            Location of the file.

        Returns
        -------
        None

        """
        BRepTools.breptools.Write(self.native_brep, str(filepath))

    def to_step(
        self,
        filepath: Union[str, pathlib.Path],
        unit: str = "MM",
        author: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        organization: Optional[str] = None,
    ) -> None:
        """
        Write the BRep shape to a STEP file.

        Parameters
        ----------
        filepath
            Location of the file.
        unit
            Base units for the geometry in the file.

        Returns
        -------
        None

        """
        writer = STEPControl.STEPControl_Writer()

        Interface.Interface_Static.SetCVal("write.step.unit", unit)
        Interface.Interface_Static.SetCVal("write.step.product.name", name or self.name)

        writer.Transfer(self.occ_shape, STEPControl.STEPControl_StepModelType.STEPControl_AsIs)  # type: ignore

        if author or description or organization:
            model = writer.Model()
            model.ClearHeader()

            header = APIHeaderSection.APIHeaderSection_MakeHeader()

            if author:
                header.SetAuthorValue(1, TCollection.TCollection_HAsciiString(author))
            if organization:
                org = Interface.Interface_HArray1OfHAsciiString(1, 1)
                org.SetValue(1, TCollection.TCollection_HAsciiString(organization))
            if description:
                desc = Interface.Interface_HArray1OfHAsciiString(1, 1)
                desc.SetValue(1, TCollection.TCollection_HAsciiString(description))

            model.AddHeaderEntity(header.FnValue())
            model.AddHeaderEntity(header.FsValue())
            model.AddHeaderEntity(header.FdValue())

        status = writer.Write(str(filepath))
        assert status == IFSelect.IFSelect_RetDone, status

    def to_stl(
        self,
        filepath: Union[str, pathlib.Path],
        linear_deflection: float = 1e-3,
        angular_deflection: float = 0.5,
    ) -> bool:
        """
        Write the BRep shape to a STL file.

        Parameters
        ----------
        filepath
            Location of the file.
        linear_deflection
            Allowable deviation between curved geometry and mesh discretisation.
        angular_deflection
            Maximum angle between two adjacent facets.

        Returns
        -------
        None

        """
        BRepMesh.BRepMesh_IncrementalMesh(self.occ_shape, linear_deflection, False, angular_deflection, True)
        stl_writer = StlAPI.StlAPI_Writer()
        stl_writer.SetASCIIMode(True)
        return stl_writer.Write(self.occ_shape, str(filepath))

    def to_iges(self, filepath: Union[str, pathlib.Path]) -> bool:
        """
        Write the BRep shape to a IGES file.

        Parameters
        ----------
        filepath
            Location of the file.

        Returns
        -------
        None

        """
        iges_writer = IGESControl.IGESControl_Writer()
        if not iges_writer.AddShape(self.occ_shape):
            raise Exception("Failed to add shape to IGES writer.")
        iges_writer.ComputeModel()
        return iges_writer.Write(str(filepath))

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_box(cls, box: compas.geometry.Box) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS box.

        Parameters
        ----------
        box

        Returns
        -------
        OCCBrep

        """
        xaxis = box.frame.xaxis.scaled(-0.5 * box.xsize)
        yaxis = box.frame.yaxis.scaled(-0.5 * box.ysize)
        zaxis = box.frame.zaxis.scaled(-0.5 * box.zsize)
        frame = box.frame.transformed(Translation.from_vector(xaxis + yaxis + zaxis))
        ax2 = frame_to_occ_ax2(frame)
        shape = BRepPrimAPI.BRepPrimAPI_MakeBox(ax2, box.xsize, box.ysize, box.zsize).Shape()
        return cls.from_native(shape)

    @classmethod
    def from_brepfaces(cls, faces: list[OCCBrepFace], solid: bool = True) -> "OCCBrep":
        """
        Make a BRep from a list of BRep faces forming an open or closed shell.

        Parameters
        ----------
        faces
            The input faces.
        solid
            Flag indicating that if the resulting shape should be converted to a solid, if possible.

        Returns
        -------
        OCCBrep

        """
        shell = TopoDS.TopoDS_Shell()
        builder = BRep.BRep_Builder()
        builder.MakeShell(shell)
        for face in faces:
            if not face.is_valid():
                face.fix()
            builder.Add(shell, face.occ_face)
        brep = cls.from_native(shell)
        brep.heal()
        if solid:
            brep.make_solid()
        return brep

    @classmethod
    def from_breps(cls, breps: list["OCCBrep"]) -> "OCCBrep":
        """
        Construct one compound BRep out of multiple individual BReps.
        """
        compound = TopoDS.TopoDS_Compound()
        builder = BRep.BRep_Builder()
        builder.MakeCompound(compound)
        for brep in breps:
            builder.Add(compound, brep.native_brep)
        return cls.from_native(compound)

    @classmethod
    def from_cone(cls, cone: compas.geometry.Cone) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS cone.

        Parameters
        ----------
        cone
            A COMPAS cone.

        Returns
        -------
        OCCBrep

        """
        raise NotImplementedError

    @classmethod
    def from_curves(cls, curves: list[compas.geometry.NurbsCurve]) -> "OCCBrep":
        """
        Construct a BRep from a set of curves.

        Parameters
        ----------
        curves
            The input curves.

        Returns
        -------
        OCCBrep
            The resulting BRep.

        """
        raise NotImplementedError

    @classmethod
    def from_cylinder(cls, cylinder: compas.geometry.Cylinder) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS cylinder.

        Parameters
        ----------
        cylinder
            A COMPAS cylinder.

        Returns
        -------
        OCCBrep

        """
        height = cylinder.height
        radius = cylinder.radius
        frame = cylinder.frame
        ax2 = frame_to_occ_ax2(frame)
        ax2.Translate(vector_to_occ(frame.zaxis * (-0.5 * height)))
        shape = BRepPrimAPI.BRepPrimAPI_MakeCylinder(ax2, radius, height).Shape()
        return cls.from_native(shape)

    @classmethod
    def from_extrusion(
        cls,
        profile: Union[OCCBrepEdge, OCCBrepFace],
        vector: Vector,
        cap_ends: bool = False,
    ) -> "OCCBrep":
        """
        Construct a BRep by extruding a closed curve along a direction vector.

        Parameters
        ----------
        profile
            The base profile of the extrusion.
        vector
            The extrusion vector.
            The extrusion has the same height as the length vector.
        cap_ends
            Flag indicating that the ends of the brep should be capped.
            Currently this flag is not supported.

        Returns
        -------
        OCCBrep

        """
        if cap_ends:
            raise NotImplementedError

        brep = cls()
        brep.native_brep = BRepPrimAPI.BRepPrimAPI_MakePrism(
            profile.occ_shape,
            vector_to_occ(vector),
        ).Shape()
        return brep

    @classmethod
    def from_loft(
        cls,
        curves: list[OCCCurve],
        start: Optional[Point] = None,
        end: Optional[Point] = None,
    ) -> "OCCBrep":
        """Construct a Brep by lofing through a sequence of curves.

        Parameters
        ----------
        curves
            The loft curves.
        start
            The start point of the loft.
        end
            The end point of the loft.

        Returns
        -------
        OCCBrep

        """
        thru = BRepOffsetAPI.BRepOffsetAPI_ThruSections(False, False)
        if start:
            thru.AddVertex(OCCBrepVertex.from_point(start).native_vertex)
        for curve in curves:
            thru.AddWire(OCCBrepLoop.from_edges([OCCBrepEdge.from_curve(curve)]).occ_wire)
        if end:
            thru.AddVertex(OCCBrepVertex.from_point(end).native_vertex)
        thru.Build()
        return Brep.from_native(thru.Shape())

    @classmethod
    def from_mesh(cls, mesh: compas.datastructures.Mesh, solid: bool = True) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS mesh.

        Parameters
        ----------
        mesh
            The input mesh.
        solid
            Flag indicating that if the resulting shape should be converted to a solid, if possible.

        Returns
        -------
        OCCBrep

        """
        shell = TopoDS.TopoDS_Shell()
        builder = BRep.BRep_Builder()
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
        brep.heal()
        if solid:
            brep.make_solid()
        return brep

    @classmethod
    def from_native(cls, shape: TopoDS.TopoDS_Shape) -> "OCCBrep":
        """
        Construct a BRep from an OCC shape.

        Parameters
        ----------
        shape
            The OCC shape.

        Returns
        -------
        OCCBrep

        """
        return cls.from_shape(shape)

    @classmethod
    def from_polygons(cls, polygons: list[compas.geometry.Polygon], solid: bool = True) -> "OCCBrep":
        """
        Construct a BRep from a set of polygons.

        Parameters
        ----------
        polygons
            The input polygons.
        solid
            Flag indicating that if the resulting shape should be converted to a solid, if possible.

        Returns
        -------
        OCCBrep

        """
        shell = TopoDS.TopoDS_Shell()
        builder = BRep.BRep_Builder()
        builder.MakeShell(shell)
        for points in polygons:
            if len(points) == 3:
                builder.Add(shell, triangle_to_face(points))
            elif len(points) == 4:
                builder.Add(shell, quad_to_face(points))
            else:
                builder.Add(shell, ngon_to_face(points))
        brep = cls.from_native(shell)
        brep.heal()
        if solid:
            brep.make_solid()
        return brep

    # @classmethod
    # def from_pipe(cls) -> "OCCBrep":
    #     pass

    @classmethod
    def from_plane(
        cls,
        plane: Plane,
        domain_u: tuple[float, float] = (-1.0, +1.0),
        domain_v: tuple[float, float] = (-1.0, +1.0),
    ) -> "OCCBrep":
        """
        Make a BRep from a plane.

        Parameters
        ----------
        plane
            A COMPAS plane.
        domain_u
            The domain of the plane in the U direction.
        domain_v
            The domain of the plane in the V direction.

        Returns
        -------
        OCCBrep

        """
        return cls.from_brepfaces([OCCBrepFace.from_plane(plane, domain_u=domain_u, domain_v=domain_v)])

    @classmethod
    def from_planes(cls, planes: list[Plane], solid: bool = True) -> "OCCBrep":
        """
        Make a BRep from a list of planes.

        Parameters
        ----------
        planes
            The input planes.
        solid
            Flag indicating that if the resulting shape should be converted to a solid, if possible.

        Returns
        -------
        OCCBrep

        """
        faces = []
        for plane in planes:
            faces.append(OCCBrepFace.from_plane(plane))
        return cls.from_brepfaces(faces, solid=solid)

    @classmethod
    def from_shape(cls, shape: TopoDS.TopoDS_Shape) -> "OCCBrep":
        """
        Construct a BRep from an OCC shape.

        Parameters
        ----------
        shape
            The OCC shape.

        Returns
        -------
        OCCBrep

        """
        brep = cls()
        brep.native_brep = shape
        return brep

    @classmethod
    def from_sphere(cls, sphere: compas.geometry.Sphere) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS sphere.

        Parameters
        ----------
        sphere
            A COMPAS sphere.

        Returns
        -------
        OCCBrep

        """
        shape = BRepPrimAPI.BRepPrimAPI_MakeSphere(gp.gp_Pnt(*sphere.frame.point), sphere.radius).Shape()
        return cls.from_native(shape)

    @classmethod
    def from_surface(
        cls,
        surface: Union[compas.geometry.Surface, OCCNurbsSurface],
        domain_u: Optional[tuple[float, float]] = None,
        domain_v: Optional[tuple[float, float]] = None,
        precision: float = 1e-6,
        loop: Optional[OCCBrepLoop] = None,
        inside: bool = True,
    ) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS surface.

        Parameters
        ----------
        surface
            The input surface.
        domain_u
            The domain of the surface in the U direction.
        domain_v
            The domain of the surface in the V direction.
        precision
            The precision of the discretisation of the surface.
        loop
            The loop to trim the surface with.
        inside
            Whether to keep the inside or outside of the loop.

        Returns
        -------
        OCCBrep

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
        brep.native_brep = BRepOffsetAPI.BRepOffsetAPI_MakePipe(
            path.occ_wire,
            profile.occ_shape,
        ).Shape()
        return brep

    @classmethod
    def from_torus(cls, torus: compas.geometry.Torus) -> "OCCBrep":
        """
        Construct a BRep from a COMPAS torus.

        Parameters
        ----------
        torus
            A COMPAS torus.

        Returns
        -------
        OCCBrep

        """
        frame = torus.frame
        ax2 = frame_to_occ_ax2(frame)
        shape = BRepPrimAPI.BRepPrimAPI_MakeTorus(ax2, torus.radius_axis, torus.radius_pipe).Shape()
        return cls.from_native(shape)

    # create patch
    # create offset

    # ==============================================================================
    # Boolean Constructors
    # ==============================================================================

    @classmethod
    def from_boolean_difference(
        cls,
        A: Union["OCCBrep", list["OCCBrep"]],
        B: Union["OCCBrep", list["OCCBrep"]],
        tol=None,
    ) -> "OCCBrep":
        """
        Construct a BRep from the boolean difference of two other BReps.

        Parameters
        ----------
        A
            A OCCBrep or list of OCCBreps to subtract from.
        B
            A OCCBrep or list of OCCBreps to subtract.

        Returns
        -------
        OCCBrep

        """
        tol = tol or TOL.absolute
        LA = TopTools.TopTools_ListOfShape()
        LB = TopTools.TopTools_ListOfShape()

        if isinstance(A, list):
            for a in A:
                LA.Append(a.native_brep)
        else:
            LA.Append(A.native_brep)

        if isinstance(B, list):
            for b in B:
                LB.Append(b.native_brep)
        else:
            LB.Append(B.native_brep)

        cut = BRepAlgoAPI.BRepAlgoAPI_Cut()
        cut.SetArguments(LA)
        cut.SetTools(LB)
        cut.SetFuzzyValue(tol)
        cut.SetRunParallel(False)
        cut.Build()

        brep = cls.from_native(cut.Shape())
        brep.sew()
        brep.fix()
        brep.make_solid()
        return brep

    @classmethod
    def from_boolean_intersection(
        cls,
        A: Union["OCCBrep", list["OCCBrep"]],
        B: Union["OCCBrep", list["OCCBrep"]],
        tol=None,
    ) -> "OCCBrep":
        """
        Construct a BRep from the boolean intersection of two other BReps.

        Parameters
        ----------
        A
            A OCCBrep or list of OCCBreps.
        B
            A OCCBrep or list of OCCBreps.

        Returns
        -------
        OCCBrep

        Raises
        ------
        BrepBooleanError

        """
        tol = tol or TOL.absolute
        LA = TopTools.TopTools_ListOfShape()
        LB = TopTools.TopTools_ListOfShape()

        if isinstance(A, list):
            for a in A:
                LA.Append(a.native_brep)
        else:
            LA.Append(A.native_brep)

        if isinstance(B, list):
            for b in B:
                LB.Append(b.native_brep)
        else:
            LB.Append(B.native_brep)

        common = BRepAlgoAPI.BRepAlgoAPI_Common()
        common.SetArguments(LA)
        common.SetTools(LB)
        common.SetFuzzyValue(tol)
        common.SetRunParallel(False)
        common.Build()

        if not common.IsDone():
            raise BrepBooleanError("Boolean intersection operation could not be completed.")

        brep = cls.from_native(common.Shape())
        brep.heal()
        brep.make_solid()
        return brep

    @classmethod
    def from_boolean_union(
        cls,
        A: Union["OCCBrep", list["OCCBrep"]],
        B: Union["OCCBrep", list["OCCBrep"]],
        tol=None,
    ) -> "OCCBrep":
        """
        Construct a BRep from the boolean union of two other BReps.

        Parameters
        ----------
        A
            A OCCBrep or list of OCCBreps.
        B
            A OCCBrep or list of OCCBreps.

        Returns
        -------
        OCCBrep

        Raises
        ------
        BrepBooleanError

        """
        tol = tol or TOL.absolute
        LA = TopTools.TopTools_ListOfShape()
        LB = TopTools.TopTools_ListOfShape()

        if isinstance(A, list):
            for a in A:
                LA.Append(a.native_brep)
        else:
            LA.Append(A.native_brep)

        if isinstance(B, list):
            for b in B:
                LB.Append(b.native_brep)
        else:
            LB.Append(B.native_brep)

        fuse = BRepAlgoAPI.BRepAlgoAPI_Fuse()
        fuse.SetArguments(LA)
        fuse.SetTools(LB)
        fuse.SetFuzzyValue(tol)
        fuse.SetRunParallel(False)
        fuse.Build()

        if not fuse.IsDone():
            raise BrepBooleanError("Boolean fuse operation could not be completed.")

        brep = cls.from_native(fuse.Shape())
        brep.heal()
        brep.make_solid()
        return brep

    # ==============================================================================
    # Converters
    # ==============================================================================

    def to_tesselation(
        self,
        linear_deflection: Optional[float] = None,
        angular_deflection: Optional[float] = None,
    ) -> tuple[Mesh, list[Polyline]]:
        """
        Create a tesselation of the shape for visualisation.

        Parameters
        ----------
        linear_deflection
            Allowable "distance" deviation between curved geometry and mesh discretisation.
        angular_deflection
            Allowable "curvature" deviation between curved geometry and mesh discretisation.

        Returns
        -------
        tuple[Mesh, list[Polyline]]

        """
        linear_deflection = linear_deflection or TOL.lineardeflection
        angular_deflection = angular_deflection or TOL.angulardeflection

        mesh = Mesh()
        polylines = []
        seen = []

        BRepMesh.BRepMesh_IncrementalMesh(self.occ_shape, linear_deflection, False, angular_deflection, True)
        bt = BRep.BRep_Tool()

        for face in self.faces:
            location = TopLoc.TopLoc_Location()
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
                    pot = bt.PolygonOnTriangulation(edge.occ_edge, triangulation, location)
                    if pot is None:
                        continue
                    points = []
                    nodes = pot.Nodes()
                    for i in range(1, pot.NbNodes() + 1):
                        node = nodes.Value(i)
                        points.append(vertices[node - 1])
                    polylines.append(Polyline(points))

        # This might not be necssary
        lines = []
        for edge in self.edges:
            if any(edge.is_same(e) for e in seen):
                continue
            if edge.is_line:
                lines.append(Polyline([edge.vertices[0].point, edge.vertices[-1].point]))
            elif edge.is_circle:
                lines.append(edge.curve.to_polyline())
            elif edge.is_ellipse:
                lines.append(edge.curve.to_polyline())
            elif edge.is_bspline:
                lines.append(edge.curve.to_polyline())

        polylines += lines
        return mesh, polylines

    def to_meshes(self, u: int = 16, v: int = 16) -> list[Mesh]:
        """
        Convert the faces of the BRep shape to meshes.

        Parameters
        ----------
        u
            The number of mesh faces in the U direction of the underlying surface geometry of every face of the Brep.
        v
            The number of mesh faces in the V direction of the underlying surface geometry of every face of the Brep.

        Returns
        -------
        list[Mesh]

        """
        converter = BRepBuilderAPI.BRepBuilderAPI_NurbsConvert(self.occ_shape, False)
        brep = OCCBrep.from_shape(converter.Shape())
        meshes = []
        for face in brep.faces:
            srf = OCCNurbsSurface.from_face(face.occ_face)
            mesh = srf.to_tesselation()
            meshes.append(mesh)
        return meshes

    def to_polygons(self) -> list[Polygon]:
        """
        Convert the faces of the BRep to simple polygons without underlying geometry.

        Returns
        -------
        list[Polygon]

        """
        polygons = []
        for face in self.faces:
            points = []
            for vertex in face.loops[0].vertices:
                points.append(vertex.point)
            polygons.append(Polygon(points))
        return polygons

    def to_viewmesh(
        self,
        linear_deflection: Optional[float] = None,
        angular_deflection: Optional[float] = None,
    ) -> tuple[compas.datastructures.Mesh, list[compas.geometry.Polyline]]:
        """
        Convert the BRep to a view mesh.

        Parameters
        ----------
        linear_deflection
            Allowable "distance" deviation between curved geometry and mesh discretisation.
        angular_deflection
            Allowable "curvature" deviation between curved geometry and mesh discretisation.

        Returns
        -------
        tuple[Mesh, list[Polyline]]
        """
        return self.to_tesselation(linear_deflection=linear_deflection, angular_deflection=angular_deflection)

    # ==============================================================================
    # Relationships
    # ==============================================================================

    def vertex_neighbors(self, vertex: OCCBrepVertex) -> list[OCCBrepVertex]:
        """
        Identify the neighbouring vertices of a given vertex.

        Parameters
        ----------
        vertex
            A vertex of the Brep.

        Returns
        -------
        list[OCCBrepVertex]
            The neighbouring vertices of the given vertex.

        """
        map = TopTools.TopTools_IndexedDataMapOfShapeListOfShape()
        TopExp.topexp.MapShapesAndUniqueAncestors(self.occ_shape, TopAbs.TopAbs_VERTEX, TopAbs.TopAbs_EDGE, map)  # type: ignore
        results = map.FindFromKey(vertex.occ_vertex)
        iterator = TopTools.TopTools_ListIteratorOfListOfShape(results)  # type: ignore
        vertices = []
        while iterator.More():
            edge = TopoDS.topods.Edge(iterator.Value())
            edge = OCCBrepEdge(edge)
            iterator.Next()
            if not edge.first_vertex.occ_vertex.IsSame(vertex.occ_vertex):
                vertices.append(edge.first_vertex)
            else:
                vertices.append(edge.last_vertex)
        return vertices

    def vertex_edges(self, vertex: OCCBrepVertex) -> list[OCCBrepEdge]:
        """
        Identify the edges connected to a given vertex.

        Parameters
        ----------
        vertex
            A vertex of the Brep

        Returns
        -------
        list[OCCBrepEdge]
            The edges connected to the given vertex.

        """
        map = TopTools.TopTools_IndexedDataMapOfShapeListOfShape()
        TopExp.topexp.MapShapesAndUniqueAncestors(self.occ_shape, TopAbs.TopAbs_VERTEX, TopAbs.TopAbs_EDGE, map)  # type: ignore
        results = map.FindFromKey(vertex.occ_vertex)
        iterator = TopTools.TopTools_ListIteratorOfListOfShape(results)  # type: ignore
        edges = []
        while iterator.More():
            edge = iterator.Value()
            edges.append(OCCBrepEdge(edge))
            iterator.Next()
        return edges

    def vertex_faces(self, vertex: OCCBrepVertex) -> list[OCCBrepFace]:
        """
        Identify the faces connected to a vertex.

        Parameters
        ----------
        vertex
            A vertex of the Brep.

        Returns
        -------
        list[OCCBrepFace]
            The faces connected to the given vertex.

        """
        map = TopTools.TopTools_IndexedDataMapOfShapeListOfShape()
        TopExp.topexp.MapShapesAndUniqueAncestors(self.occ_shape, TopAbs.TopAbs_VERTEX, TopAbs.TopAbs_FACE, map)  # type: ignore
        results = map.FindFromKey(vertex.occ_vertex)
        iterator = TopTools.TopTools_ListIteratorOfListOfShape(results)  # type: ignore
        faces = []
        while iterator.More():
            face = iterator.Value()
            faces.append(OCCBrepFace(face))
            iterator.Next()
        return faces

    def edge_faces(self, edge: OCCBrepEdge) -> list[OCCBrepFace]:
        """
        Identify the faces connected to an edge.

        Parameters
        ----------
        edge
            An edge of the Brep.

        Returns
        -------
        list[OCCBrepFace]
            The faces connected to the given edge.

        """
        map = TopTools.TopTools_IndexedDataMapOfShapeListOfShape()
        TopExp.topexp.MapShapesAndUniqueAncestors(self.occ_shape, TopAbs.TopAbs_EDGE, TopAbs.TopAbs_FACE, map)  # type: ignore
        results = map.FindFromKey(edge.occ_edge)
        iterator = TopTools.TopTools_ListIteratorOfListOfShape(results)  # type: ignore
        faces = []
        while iterator.More():
            face = iterator.Value()
            faces.append(OCCBrepFace(face))
            iterator.Next()
        return faces

    def edge_loops(self, edge: OCCBrepEdge) -> list[OCCBrepLoop]:
        """Identify the parent loops of an edge.

        Parameters
        ----------
        edge
            An edge of the Brep.

        Returns
        -------
        list[OCCBrepLoop]
            The loops containing the given edge.

        """

        map = TopTools.TopTools_IndexedDataMapOfShapeListOfShape()
        TopExp.topexp.MapShapesAndUniqueAncestors(self.occ_shape, TopAbs.TopAbs_EDGE, TopAbs.TopAbs_WIRE, map)  # type: ignore
        results = map.FindFromKey(edge.occ_edge)
        iterator = TopTools.TopTools_ListIteratorOfListOfShape(results)  # type: ignore
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

    def boolean_difference(self, *others: "OCCBrep", tol=None) -> "OCCBrep":
        """Return the boolean difference of this shape and a collection of other shapes.

        Parameters
        ----------
        others
            A collection of other BRep shapes to subtract from the current shape.

        Results
        -------
        OCCBrep
            The difference between the current shape and the other shapes.

        Raises
        ------
        BrepBooleanError

        """
        tol = tol or TOL.absolute
        LA = TopTools.TopTools_ListOfShape()
        LB = TopTools.TopTools_ListOfShape()

        LA.Append(self.native_brep)

        for b in others:
            LB.Append(b.native_brep)

        cut = BRepAlgoAPI.BRepAlgoAPI_Cut()
        cut.SetArguments(LA)
        cut.SetTools(LB)
        cut.SetFuzzyValue(tol)
        cut.SetRunParallel(False)
        cut.Build()

        if not cut.IsDone():
            raise BrepBooleanError("Boolean difference operation could not be completed.")

        cls = type(self)
        brep = cls.from_native(cut.Shape())
        brep.heal()
        brep.make_solid()
        return brep

    def boolean_intersection(self, *others: "OCCBrep", tol=None) -> "OCCBrep":
        """Return the boolean intersection of the current shape and a collection of other shapes.

        Parameters
        ----------
        others
            A collection of other BRep shapes to intersect with the current shape.

        Returns
        -------
        OCCBrep
            The intersection between the current shape and the others.

        Raises
        ------
        BrepBooleanError

        """
        tol = tol or TOL.absolute
        LA = TopTools.TopTools_ListOfShape()
        LB = TopTools.TopTools_ListOfShape()

        LA.Append(self.native_brep)

        for b in others:
            LB.Append(b.native_brep)

        common = BRepAlgoAPI.BRepAlgoAPI_Common()
        common.SetArguments(LA)
        common.SetTools(LB)
        common.SetFuzzyValue(tol)
        common.SetRunParallel(False)
        common.Build()

        if not common.IsDone():
            raise BrepBooleanError("Boolean intersection operation could not be completed.")

        cls = type(self)
        brep = cls.from_native(common.Shape())
        brep.heal()
        brep.make_solid()
        return brep

    def boolean_union(self, *others: "OCCBrep", tol=None) -> "OCCBrep":
        """Return the boolean union of the current shape and a collection of other shapes.

        Parameters
        ----------
        others
            A collection of other BRep shapes to unite with the current shape.

        Returns
        -------
        OCCBrep
            The union between the current shape and the others.

        Raises
        ------
        BrepBooleanError

        """
        tol = tol or TOL.absolute
        LA = TopTools.TopTools_ListOfShape()
        LB = TopTools.TopTools_ListOfShape()

        LA.Append(self.native_brep)

        for b in others:
            LB.Append(b.native_brep)

        fuse = BRepAlgoAPI.BRepAlgoAPI_Fuse()
        fuse.SetArguments(LA)
        fuse.SetTools(LB)
        fuse.SetFuzzyValue(tol)
        fuse.SetRunParallel(False)
        fuse.Build()

        if not fuse.IsDone():
            raise BrepBooleanError("Boolean fuse operation could not be completed.")

        cls = type(self)
        brep = cls.from_native(fuse.Shape())
        brep.heal()
        brep.make_solid()
        return brep

    def check(self):
        """
        Check the shape.

        Returns
        -------
        None

        """
        if self.type == TopAbs.TopAbs_SHELL:
            check = BRepCheck.BRepCheck_Shell(self.occ_shape)  # type: ignore
            print(BRepCheck.BRepCheck_Status(check.Closed()))
            print(BRepCheck.BRepCheck_Status(check.Orientation()))

    def contours(self, planes: list[compas.geometry.Plane]) -> list[list[compas.geometry.Polyline]]:
        """
        Generate contour lines by slicing the BRep shape with a series of planes.

        Parameters
        ----------
        planes
            The slicing planes.

        Returns
        -------
        list[list[compas.geometry.Polyline]]
            A list of polylines per plane.

        """
        raise NotImplementedError

    def cull_unused_vertices(self) -> None:
        """
        Remove all unused vertices.

        Returns
        -------
        None

        """
        raise NotImplementedError

    def cull_unused_edges(self) -> None:
        """
        Remove all unused edges.

        Returns
        -------
        None

        """
        raise NotImplementedError

    def cull_unused_loops(self) -> None:
        """
        Remove all unused loops.

        Returns
        -------
        None

        """
        raise NotImplementedError

    def cull_unused_faces(self) -> None:
        """
        Remove all unused faces.

        Returns
        -------
        None

        """
        raise NotImplementedError

    def fillet(
        self,
        radius: float,
        exclude: Optional[list[OCCBrepEdge]] = None,
    ) -> None:
        """Fillet the edges of a BRep.

        Parameters
        ----------
        radius
            The radius of the fillet.
        exclude
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
        fillet = BRepFilletAPI.BRepFilletAPI_MakeFillet(self.occ_shape)
        for edge in self.edges:
            if exclude:
                if any(e.is_same(edge) for e in exclude):
                    continue
            fillet.Add(radius, edge.occ_edge)
        fillet.Build()
        if not fillet.IsDone():
            raise BrepFilletError("Fillet operation could not be completed.")
        self.occ_shape = fillet.Shape()

    def filleted(self, radius: float, exclude: Optional[list[OCCBrepEdge]] = None) -> "OCCBrep":
        """Construct a copy of a Brep with filleted edges.

        Parameters
        ----------
        radius
            The radius of the fillet.
        exclude
            A list of edges to exclude from the fillet operation.

        Returns
        -------
        OCCBrep

        """
        brep = self.copy()
        brep.fillet(radius, exclude=exclude)
        return brep

    def fix(self):
        """
        Fix the shell.

        Returns
        -------
        None

        """
        if self.type == TopAbs.TopAbs_SHELL:
            fixer = ShapeFix.ShapeFix_Shell(self.occ_shape)  # type: ignore
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

    def intersect(self, other: "OCCBrep") -> Union["OCCBrep", None]:
        """Intersect this Brep with another.

        Parameters
        ----------
        other
            The other brep.

        Returns
        -------
        OCCBrep
            If it exists, the intersection is a curve
            that can be accessed via the edges of the returned brep.

        """
        section = BRepAlgoAPI.BRepAlgoAPI_Section(self.occ_shape, other.occ_shape)
        section.Build()
        if section.IsDone():
            occ_shape = section.Shape()
            return OCCBrep.from_native(occ_shape)

    def make_positive(self):
        """Make the volume of a closed brep positive if it is not.

        Returns
        -------
        None

        """
        if self.is_closed:
            if self.volume < 0.0:
                self.native_brep.Reverse()

    def make_solid(self):
        """
        Convert the current shape to a solid if it is a shell.

        Returns
        -------
        None

        """
        if self.type == TopAbs.TopAbs_SHELL:
            # self.occ_shape = BRepBuilderAPI.BRepBuilderAPI_MakeSolid(self.occ_shape).Shape()  # type: ignore
            fixer = ShapeFix.ShapeFix_Solid()
            self.occ_shape = fixer.SolidFromShell(self.occ_shape)  # type: ignore

    def overlap(
        self,
        other: "OCCBrep",
        linear_deflection: Optional[float] = None,
        angular_deflection: Optional[float] = None,
        tolerance: float = 0.0,
        relative: bool = False,
    ) -> tuple[list[OCCBrepFace], list[OCCBrepFace]]:
        """
        Compute the overlap between this BRep and another.

        Parameters
        ----------
        other
            The other brep.
        linear_deflection
            Maximum linear deflection for shape approximation.
        angular_deflection
            Maximum angular deflection for shape approximation.
        tolerance
            Allowable deviation between shapes.

        Other Parameters
        ----------------
        relative
            If True, linear deflection used for faces is the maximum linear deflection of their edges.

        Returns
        -------
        tuple[list[OCCBrepFace], list[OCCBrepFace]]

        """
        linear_deflection = linear_deflection or TOL.lineardeflection
        angular_deflection = angular_deflection or TOL.angulardeflection

        mesher1 = BRepMesh.BRepMesh_IncrementalMesh(self.native_brep, linear_deflection, relative, angular_deflection, False)
        mesher2 = BRepMesh.BRepMesh_IncrementalMesh(other.native_brep, linear_deflection, relative, angular_deflection, False)
        mesher1.Perform()
        mesher2.Perform()
        proximity = BRepExtrema.BRepExtrema_ShapeProximity(self.native_brep, other.native_brep)
        proximity.SetTolerance(tolerance)
        proximity.Perform()

        overlaps1 = proximity.OverlapSubShapes1()
        keys1 = overlaps1.Keys()
        faces1 = []
        for key in keys1:
            face = proximity.GetSubShape1(key)
            faces1.append(OCCBrepFace(face))  # type: ignore

        overlaps2 = proximity.OverlapSubShapes2()
        keys2 = overlaps2.Keys()
        faces2 = []
        for key in keys2:
            face = proximity.GetSubShape2(key)
            faces2.append(OCCBrepFace(face))  # type: ignore

        return faces1, faces2

    def sew(self):
        """
        Sew together the individual parts of the shape.

        Returns
        -------
        None

        """
        if len(self.faces) > 1:
            sewer = BRepBuilderAPI.BRepBuilderAPI_Sewing()
            sewer.Load(self.occ_shape)
            sewer.Perform()
            self.occ_shape = sewer.SewedShape()

    def simplify(
        self,
        merge_edges: bool = True,
        merge_faces: bool = True,
        lineardeflection: Optional[float] = None,
        angulardeflection: Optional[float] = None,
    ):
        """Simplify the shape by merging colinear edges and coplanar faces.

        Parameters
        ----------
        merge_edges
            Merge edges with the same underlying geometry.
        merge_faces
            Merge faces with the same underlying geometry.
        lineardeflection
            Default is `compas.tolerance.Tolerance.lineardeflection`.
        angulardeflection
            Default is `compas.tolerance.Tolerance.angulardeflection`.

        Returns
        -------
        None

        """
        if not merge_edges and not merge_faces:
            return

        lineardeflection = lineardeflection or TOL.lineardeflection
        angulardeflection = angulardeflection or TOL.angulardeflection

        simplifier = ShapeUpgrade.ShapeUpgrade_UnifySameDomain()
        simplifier.SetLinearTolerance(lineardeflection)
        simplifier.SetAngularTolerance(angulardeflection)
        simplifier.Initialize(self.native_brep, merge_edges, merge_faces)
        simplifier.Build()
        shape = simplifier.Shape()
        self.native_brep = shape

    def slice(self, plane: compas.geometry.Plane) -> Union["OCCBrep", None]:
        """Slice a BRep with a plane.

        Parameters
        ----------
        plane
            The slicing plane.

        Returns
        -------
        OCCBrep | None
            The resulting Brep slice or None if the plane does not intersect the Brep.

        """
        if isinstance(plane, Frame):
            plane = Plane.from_frame(plane)

        face = OCCBrepFace.from_plane(plane)
        section = BRepAlgoAPI.BRepAlgoAPI_Section(self.occ_shape, face.occ_face)
        section.Build()
        if section.IsDone():
            occ_shape = section.Shape()
            return OCCBrep.from_native(occ_shape)

    def split(self, other: "OCCBrep") -> list["OCCBrep"]:
        """Split a BRep using another BRep as splitter.

        Parameters
        ----------
        other
            Another brep.

        Returns
        -------
        list[OCCBrep]

        """
        splitter = BOPAlgo.BOPAlgo_Splitter()
        splitter.AddArgument(self.occ_shape)
        splitter.AddTool(other.occ_shape)
        splitter.Perform()
        shape = splitter.Shape()
        results: list[OCCBrep] = []
        if isinstance(shape, TopoDS.TopoDS_Compound):
            it = TopoDS.TopoDS_Iterator(shape)
            while it.More():
                results.append(OCCBrep.from_shape(it.Value()))
                it.Next()
        else:
            results.append(OCCBrep.from_shape(shape))
        return results

    def transform(self, matrix: compas.geometry.Transformation) -> None:
        """
        Transform this Brep.

        Parameters
        ----------
        matrix
            A transformation matrix.

        Returns
        -------
        None

        """
        trsf = compas_transformation_to_trsf(matrix)
        builder = BRepBuilderAPI.BRepBuilderAPI_Transform(self.occ_shape, trsf, True)
        shape = builder.ModifiedShape(self.occ_shape)
        self._occ_shape = shape

    def transformed(self, matrix: compas.geometry.Transformation) -> "OCCBrep":
        """
        Return a transformed copy of the Brep.

        Parameters
        ----------
        matrix
            A transformation matrix.

        Returns
        -------
        OCCBrep

        """
        trsf = compas_transformation_to_trsf(matrix)
        builder = BRepBuilderAPI.BRepBuilderAPI_Transform(self.occ_shape, trsf, True)
        shape = builder.ModifiedShape(self.occ_shape)
        return OCCBrep.from_shape(shape)

    def trim(self, plane: compas.geometry.Plane) -> None:
        """Trim a Brep with a plane.

        Parameters
        ----------
        plane
            The slicing plane.

        Returns
        -------
        None

        """
        if isinstance(plane, Frame):
            plane = Plane.from_frame(plane)

        arguments = [self.occ_shape]
        tools = [OCCBrepFace.from_plane(plane).occ_shape]
        results = split_shapes(arguments, tools)  # type: ignore

        occ_shape = None
        for test in results:
            point = compute_shape_centreofmass(test)
            if is_point_behind_plane(point, plane):
                occ_shape = test
                break
        if occ_shape:
            self.occ_shape = occ_shape

    def trimmed(self, plane: compas.geometry.Plane) -> "OCCBrep":
        """Construct a copy of a Brep trimmed with a plane.

        Parameters
        ----------
        plane
            The slicing plane.

        Returns
        -------
        OCCBrep

        """
        brep = self.copy()
        brep.trim(plane)
        return brep

    def offset(self, distance: float) -> "OCCBrep":
        """Construct a thickened copy of the brep.

        Parameters
        ----------
        distance
            The thickness in the form of an offset distance.

        Returns
        -------
        OCCBrep

        """
        offset = BRepOffsetAPI.BRepOffsetAPI_MakeThickSolid()
        offset.MakeThickSolidBySimple(self.native_brep, distance)
        return Brep.from_native(offset.Shape())
