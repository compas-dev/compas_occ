from math import isfinite
from math import radians
from os import PathLike
from typing import Optional
from typing import Union
from typing import cast

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
from OCC.Core import GProp
from OCC.Core import ShapeFix
from OCC.Core import ShapeUpgrade
from OCC.Core import StlAPI
from OCC.Core import TopAbs
from OCC.Core import TopExp
from OCC.Core import TopLoc
from OCC.Core import TopoDS
from OCC.Core import TopTools
from OCC.Core import gp

import compas.datastructures
import compas.geometry
from compas.data import Data
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import BrepVertex
from compas.geometry import Curve
from compas.geometry import Frame
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Polygon
from compas.geometry import Polyline
from compas.geometry import Tessellation
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
from compas_occ.occ import occ_shape_find_edges
from compas_occ.occ import occ_shape_find_faces
from compas_occ.occ import occ_shape_find_loops
from compas_occ.occ import occ_shape_find_shells
from compas_occ.occ import occ_shape_find_solids
from compas_occ.occ import occ_shape_find_vertices
from compas_occ.occ import split_shapes

from .brepedge import OCCBrepEdge
from .brepface import OCCBrepFace
from .breploop import OCCBrepLoop
from .brepvertex import OCCBrepVertex
from .errors import BrepBooleanError
from .errors import BrepFilletError
from .errors import BrepTessellationError

FilePath = Union[str, PathLike[str]]


def _fallback_edge_polyline(edge: OCCBrepEdge, segments: int = 128) -> list[Point]:
    """Sample an edge over its finite topological parameter domain."""
    try:
        supported = edge.is_line or edge.is_circle or edge.is_ellipse or edge.is_hyperbola or edge.is_parabola or edge.is_bezier or edge.is_bspline
        edge_type = edge.type
    except Exception as error:
        raise BrepTessellationError("Open CASCADE could not identify an edge for boundary sampling.") from error

    if not supported:
        raise BrepTessellationError(f"Open CASCADE boundary sampling does not support edge curve type {edge_type}.")

    try:
        start, end = edge.domain
        if not isfinite(start) or not isfinite(end):
            raise ValueError("The edge parameter domain is not finite.")
        count = 1 if edge.is_line else segments
        points = [point_to_compas(edge.occ_adaptor.Value(start + (end - start) * index / count)) for index in range(count + 1)]
        first = edge.first_vertex.point
        last = edge.last_vertex.point
    except Exception as error:
        raise BrepTessellationError(f"Open CASCADE could not sample boundary edge curve type {edge_type}.") from error

    distance_to_first = sum((a - b) ** 2 for a, b in zip(points[0], first))
    reverse_distance_to_first = sum((a - b) ** 2 for a, b in zip(points[-1], first))
    if TOL.is_close(distance_to_first, reverse_distance_to_first):
        if edge.orientation == TopAbs.TopAbs_REVERSED:
            points.reverse()
    elif reverse_distance_to_first < distance_to_first:
        points.reverse()
    points[0] = first
    points[-1] = last
    return points


class OCCBrep(Data):
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
        return self.to_data(include_native=True)

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
        return cls.from_data(data)

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

    def copy(self, cls: Optional[type] = None, copy_guid: bool = False) -> "OCCBrep":
        """Deep-copy this BRep using the native OCC copying mechanism.

        Parameters
        ----------
        cls
            The type of BRep implementation to return.
        copy_guid
            If `True`, copy the data object identifier.

        Returns
        -------
        OCCBrep

        """
        builder = BRepBuilderAPI.BRepBuilderAPI_Copy(self.occ_shape)
        builder.Perform(self.occ_shape)
        target_cls = cls or type(self)
        brep = target_cls.from_native(builder.Shape())
        brep.name = self.name
        if copy_guid:
            brep._guid = self.guid
        return brep

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
    def is_valid(self) -> bool:
        return BRepCheck.BRepCheck_Analyzer(self.occ_shape).IsValid()

    @property
    def is_orientable(self) -> bool:
        """Whether the BRep is orientable.

        Raises
        ------
        NotImplementedError
            OCC does not currently compute this semantic property.

        """
        raise NotImplementedError("OCC does not compute whether a BRep is orientable.")

    @property
    def is_closed(self) -> bool:
        """Whether the BRep has no naked boundaries.

        Raises
        ------
        NotImplementedError
            OCC does not currently compute this semantic property.

        """
        raise NotImplementedError("OCC does not compute whether a BRep has naked boundaries.")

    @property
    def is_infinite(self) -> bool:
        """Whether the BRep is infinite.

        Raises
        ------
        NotImplementedError
            OCC does not currently compute this semantic property.

        """
        raise NotImplementedError("OCC does not compute whether a BRep is infinite.")

    @property
    def is_convex(self) -> bool:
        """Whether the BRep is convex.

        Raises
        ------
        NotImplementedError
            OCC does not currently compute this semantic property.

        """
        raise NotImplementedError("OCC does not compute whether a BRep is convex.")

    @property
    def is_manifold(self) -> bool:
        """Whether the BRep is manifold.

        Raises
        ------
        NotImplementedError
            OCC does not currently compute this semantic property.

        """
        raise NotImplementedError("OCC does not compute whether a BRep is manifold.")

    @property
    def is_surface(self) -> bool:
        """Whether the BRep consists of a single face."""
        return self.type == TopAbs.TopAbs_FACE

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
            self._vertices = [OCCBrepVertex(vertex) for vertex in occ_shape_find_vertices(self.occ_shape)]
        return self._vertices

    @property
    def edges(self) -> list[OCCBrepEdge]:
        if self._edges is None:
            self._edges = [OCCBrepEdge(edge) for edge in occ_shape_find_edges(self.occ_shape)]
        return self._edges

    @property
    def loops(self) -> list[OCCBrepLoop]:
        if self._loops is None:
            self._loops = [OCCBrepLoop(wire) for wire in occ_shape_find_loops(self.occ_shape)]
        return self._loops

    @property
    def faces(self) -> list[OCCBrepFace]:
        if self._faces is None:
            self._faces = [OCCBrepFace(face) for face in occ_shape_find_faces(self.occ_shape)]
        return self._faces

    @property
    def shells(self) -> list["OCCBrep"]:
        if self._shells is None:
            self._shells = [OCCBrep.from_native(shell) for shell in occ_shape_find_shells(self.occ_shape)]
        return self._shells

    @property
    def solids(self) -> list["OCCBrep"]:
        if self._solids is None:
            self._solids = [OCCBrep.from_native(solid) for solid in occ_shape_find_solids(self.occ_shape)]
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

    def to_data(self, include_native: bool = False, units: Optional[str] = None) -> dict:
        """Convert the BRep to versioned JSON-compatible data.

        Parameters
        ----------
        include_native
            If `True`, include an exact Base64-encoded OCC BREP payload.
        units
            The unit identifier associated with the coordinates.

        Returns
        -------
        dict
            The versioned neutral schema and optional native payload.

        """
        from .serialization import brep_to_data

        return brep_to_data(self, include_native=include_native, units=units)

    @classmethod
    def from_data(
        cls,
        data: dict,
        prefer_native: bool = True,
        validate: bool = True,
        heal: bool = False,
    ) -> "OCCBrep":
        """Construct a BRep from versioned or legacy serialization data.

        Parameters
        ----------
        data
            The serialization data.
        prefer_native
            If `True`, use a compatible native payload when available.
        validate
            If `True`, reject an invalid reconstructed shape.
        heal
            If `True`, heal a neutral reconstruction before validation.

        Returns
        -------
        OCCBrep
            The reconstructed BRep.

        """
        from .serialization import brep_from_data

        brep = brep_from_data(data, prefer_native=prefer_native, validate=validate, heal=heal)
        if cls is OCCBrep:
            return brep
        return cls.from_native(brep.native_brep)

    @classmethod
    def from_brep(cls, filename: FilePath) -> "OCCBrep":
        """Construct a BRep from a native Open CASCADE BREP file.

        Parameters
        ----------
        filename
            The file path.

        Returns
        -------
        OCCBrep
            The geometry stored in the file.

        """
        from compas_occ.files import read_brep
        from compas_occ.files._geometry import shape_from_geometry

        geometries = read_brep(filename).geometries
        breps = [cls.from_native(shape_from_geometry(geometry, "BREP")) for geometry in geometries]
        if not breps:
            raise ValueError("The BREP file contains no geometries.")
        return breps[0] if len(breps) == 1 else cls.from_breps(breps)

    @classmethod
    def from_step(
        cls,
        filename: FilePath,
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
        from compas_occ.files import read_step
        from compas_occ.files._geometry import shape_from_geometry

        geometries = read_step(filename).geometries
        breps = [cls.from_native(shape_from_geometry(geometry, "STEP")) for geometry in geometries]
        if not breps:
            raise ValueError("The STEP file contains no geometries.")
        brep = breps[0] if len(breps) == 1 else cls.from_breps(breps)
        if heal:
            brep.heal()
        if solid:
            brep.make_solid()
        return brep

    @classmethod
    def from_iges(cls, filename: FilePath, solid: bool = True) -> "OCCBrep":
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
        from compas_occ.files import read_iges
        from compas_occ.files._geometry import shape_from_geometry

        geometries = read_iges(filename).geometries
        breps = [cls.from_native(shape_from_geometry(geometry, "IGES")) for geometry in geometries]
        if not breps:
            raise ValueError("The IGES file contains no geometries.")
        brep = breps[0] if len(breps) == 1 else cls.from_breps(breps)
        brep.heal()
        if solid:
            brep.make_solid()
        return brep

    def to_brep(
        self,
        filepath: FilePath,
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
        from compas_occ.files import write_brep

        write_brep(filepath, [self])

    def to_step(
        self,
        filepath: FilePath,
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
        from compas_occ.files import write_step

        write_step(
            filepath,
            [self],
            unit=unit,
            author=author,
            name=name or self.name,
            description=description,
            organization=organization,
        )

    def to_stl(
        self,
        filepath: FilePath,
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

    def to_iges(
        self,
        filepath: FilePath,
        unit: str = "MM",
        mode: int = 0,
    ) -> bool:
        """
        Write the BRep shape to a IGES file.

        Parameters
        ----------
        filepath
            Location of the file.
        unit
            Base unit for the geometry.
        mode
            IGES write mode: `0` writes faces and `1` writes BReps.

        Returns
        -------
        None

        """
        from compas_occ.files import write_iges

        write_iges(filepath, [self], unit=unit, mode=mode)
        return True

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
            if not face.is_valid:
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
        # height = cone.height
        # radius = cone.
        # frame = cone.frame
        # ax2 = frame_to_occ_ax2(frame)
        # ax2.Translate(vector_to_occ(frame.zaxis * (-0.5 * height)))
        # shape = BRepPrimAPI.BRepPrimAPI_MakeCone(ax2, radius, height).Shape()
        # return cls.from_native(shape)
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
        profile: Union[Curve, Polyline, OCCBrepEdge, OCCBrepFace],
        vector: Vector,
        cap_ends: bool = True,
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
            If ``True``, cap the planar ends of the extrusion when possible.

        Returns
        -------
        OCCBrep

        """
        if isinstance(profile, OCCBrepFace):
            if cap_ends:
                shape = profile.occ_face
            else:
                shape = TopoDS.TopoDS_Compound()
                builder = BRep.BRep_Builder()
                builder.MakeCompound(shape)
                for loop in profile.loops:
                    occ_loop = cast(OCCBrepLoop, loop)
                    builder.Add(shape, occ_loop.occ_wire)
        else:
            if isinstance(profile, Polyline):
                wire = OCCBrepLoop.from_polyline(profile).occ_wire
                shape = wire
            else:
                if isinstance(profile, OCCBrepEdge):
                    edge = profile.occ_edge
                elif isinstance(profile, OCCCurve):
                    edge = OCCBrepEdge.from_curve(profile).occ_edge
                else:
                    native_curve = getattr(profile, "native_curve", None)
                    if native_curve is None:
                        raise TypeError("The extrusion profile should be a curve, polyline, BRep edge, or BRep face.")
                    edge = OCCBrepEdge.from_curve(OCCCurve.from_native(native_curve)).occ_edge
                shape = edge
                wire_builder = BRepBuilderAPI.BRepBuilderAPI_MakeWire(edge)
                if not wire_builder.IsDone():
                    raise ValueError("The extrusion profile could not be converted to a wire.")
                wire = wire_builder.Wire()
            if cap_ends:
                face_builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(wire)
                if not face_builder.IsDone():
                    raise ValueError("Capped extrusions require a closed planar profile.")
                shape = face_builder.Face()

        brep = cls()
        brep.native_brep = BRepPrimAPI.BRepPrimAPI_MakePrism(
            shape,
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
        return OCCBrep.from_native(thru.Shape())

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
        holes: Optional[list[OCCBrepLoop]] = None,
        boundary: Optional[OCCBrepLoop] = None,
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
        holes
            Inner boundary loops.
        boundary
            The external boundary loop. This is the preferred name for
            the legacy `loop` parameter.

        Returns
        -------
        OCCBrep

        """
        face = OCCBrepFace.from_surface(
            surface,
            domain_u=domain_u,
            domain_v=domain_v,
            precision=precision,
            loop=loop,
            inside=inside,
            holes=holes,
            boundary=boundary,
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

    def to_tessellation(
        self,
        *,
        linear_deflection: float,
        angular_deflection: float,
    ) -> Tessellation:
        """Create a triangular tessellation of the trimmed BRep boundary.

        Parameters
        ----------
        linear_deflection
            The positive finite linear deflection in model units.
        angular_deflection
            The positive finite angular deflection in degrees, no greater
            than 180.

        Returns
        -------
        Tessellation
            The indexed triangles and discretized BRep edges.

        Notes
        -----
        The core `Brep.to_tessellation` facade resolves defaults and validates
        both values before plugin dispatch. This native adapter converts the
        angular value to radians exactly once at the Open CASCADE boundary.
        Boundary polylines use the face triangulation where available; edges
        without that native data are sampled over their topological parameter
        domains.

        Raises
        ------
        BrepTessellationError
            If Open CASCADE raises while meshing or retrieving a face
            triangulation, does not complete meshing, omits a face
            triangulation, or cannot sample a boundary edge fallback. Native
            exceptions are available as the exception cause.

        """
        angular_deflection_radians = radians(angular_deflection)

        vertices = []
        triangles = []
        polylines = []
        seen = []

        try:
            copy_builder = BRepBuilderAPI.BRepBuilderAPI_Copy(self.occ_shape, True, False)
            meshing_brep = type(self).from_native(copy_builder.Shape())
            mesher = BRepMesh.BRepMesh_IncrementalMesh(meshing_brep.occ_shape, linear_deflection, False, angular_deflection_radians, False)
        except Exception as error:
            raise BrepTessellationError("Open CASCADE could not start BRep meshing.") from error

        try:
            meshing_is_done = mesher.IsDone()
            meshing_status = mesher.GetStatusFlags()
        except Exception as error:
            raise BrepTessellationError("Open CASCADE could not report BRep meshing status.") from error

        if not meshing_is_done:
            raise BrepTessellationError(f"Open CASCADE BRep meshing failed with status {meshing_status}.")
        bt = BRep.BRep_Tool()

        for face_index, face in enumerate(meshing_brep.faces):
            location = TopLoc.TopLoc_Location()
            try:
                triangulation = bt.Triangulation(face.occ_face, location)
            except Exception as error:
                raise BrepTessellationError(f"Open CASCADE could not retrieve triangulation for BRep face {face_index}.") from error
            if triangulation is None:
                raise BrepTessellationError(f"Open CASCADE produced no triangulation for BRep face {face_index}; meshing status {meshing_status}.")
            nodes = []
            trsf = location.Transformation()
            for i in range(1, triangulation.NbNodes() + 1):
                nodes.append(triangulation.Node(i).Transformed(trsf))
            face_vertices = [point_to_compas(node) for node in nodes]
            offset = len(vertices)
            vertices.extend(face_vertices)
            face_triangles = triangulation.Triangles()
            for i in range(1, triangulation.NbTriangles() + 1):
                triangle = face_triangles.Value(i)
                u, v, w = triangle.Get()
                if face.orientation == TopAbs.TopAbs_REVERSED:
                    v, w = w, v
                triangles.append([offset + u - 1, offset + v - 1, offset + w - 1])
            # process the face loops to produce edges with the same discretisation as the faces
            for loop in face.loops:
                for edge in loop.edges:
                    occ_edge = cast(OCCBrepEdge, edge)
                    if any(occ_edge.is_same(e) for e in seen):
                        continue
                    pot = bt.PolygonOnTriangulation(occ_edge.occ_edge, triangulation, location)
                    if pot is None:
                        continue
                    seen.append(occ_edge)
                    points = []
                    nodes = pot.Nodes()
                    for i in range(1, pot.NbNodes() + 1):
                        node = nodes.Value(i)
                        points.append(face_vertices[node - 1])
                    polylines.append(points)

        # Edges without polygon-on-triangulation data are sampled over the
        # actual topological parameter domain.
        lines = []
        for edge in meshing_brep.edges:
            if any(edge.is_same(e) for e in seen):
                continue
            occ_edge = cast(OCCBrepEdge, edge)
            lines.append(_fallback_edge_polyline(occ_edge))
            seen.append(occ_edge)

        polylines += lines
        return Tessellation(vertices, triangles, polylines=polylines)

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

    # ==============================================================================
    # Relationships
    # ==============================================================================

    def vertex_neighbors(self, vertex: BrepVertex) -> list[OCCBrepVertex]:
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
        TopExp.topexp.MapShapesAndUniqueAncestors(
            self.occ_shape,
            TopAbs.TopAbs_ShapeEnum(TopAbs.TopAbs_VERTEX),
            TopAbs.TopAbs_ShapeEnum(TopAbs.TopAbs_EDGE),
            map,
        )
        results = map.FindFromKey(vertex.native_vertex)
        vertices = []
        for shape in results:
            edge = OCCBrepEdge(TopoDS.topods.Edge(shape))
            if not edge.first_vertex.occ_vertex.IsSame(vertex.native_vertex):
                vertices.append(edge.first_vertex)
            else:
                vertices.append(edge.last_vertex)
        return vertices

    def vertex_edges(self, vertex: BrepVertex) -> list[OCCBrepEdge]:
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
        TopExp.topexp.MapShapesAndUniqueAncestors(
            self.occ_shape,
            TopAbs.TopAbs_ShapeEnum(TopAbs.TopAbs_VERTEX),
            TopAbs.TopAbs_ShapeEnum(TopAbs.TopAbs_EDGE),
            map,
        )
        results = map.FindFromKey(vertex.native_vertex)
        edges = []
        for shape in results:
            edges.append(OCCBrepEdge(TopoDS.topods.Edge(shape)))
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
        TopExp.topexp.MapShapesAndUniqueAncestors(
            self.occ_shape,
            TopAbs.TopAbs_ShapeEnum(TopAbs.TopAbs_VERTEX),
            TopAbs.TopAbs_ShapeEnum(TopAbs.TopAbs_FACE),
            map,
        )
        results = map.FindFromKey(vertex.occ_vertex)
        faces = []
        for shape in results:
            faces.append(OCCBrepFace(TopoDS.topods.Face(shape)))
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
        TopExp.topexp.MapShapesAndUniqueAncestors(
            self.occ_shape,
            TopAbs.TopAbs_ShapeEnum(TopAbs.TopAbs_EDGE),
            TopAbs.TopAbs_ShapeEnum(TopAbs.TopAbs_FACE),
            map,
        )
        results = map.FindFromKey(edge.occ_edge)
        faces = []
        for shape in results:
            faces.append(OCCBrepFace(TopoDS.topods.Face(shape)))
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
        TopExp.topexp.MapShapesAndUniqueAncestors(
            self.occ_shape,
            TopAbs.TopAbs_ShapeEnum(TopAbs.TopAbs_EDGE),
            TopAbs.TopAbs_ShapeEnum(TopAbs.TopAbs_WIRE),
            map,
        )
        results = map.FindFromKey(edge.occ_edge)
        loops = []
        for shape in results:
            loops.append(OCCBrepLoop(TopoDS.topods.Wire(shape)))
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
            check = BRepCheck.BRepCheck_Shell(TopoDS.topods.Shell(self.occ_shape))
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
            fixer = ShapeFix.ShapeFix_Shell(TopoDS.topods.Shell(self.occ_shape))
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
        if self.occ_shape.Closed():
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
            fixer = ShapeFix.ShapeFix_Solid()
            self.occ_shape = fixer.SolidFromShell(TopoDS.topods.Shell(self.occ_shape))

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
            faces1.append(OCCBrepFace(TopoDS.topods.Face(face)))

        overlaps2 = proximity.OverlapSubShapes2()
        keys2 = overlaps2.Keys()
        faces2 = []
        for key in keys2:
            face = proximity.GetSubShape2(key)
            faces2.append(OCCBrepFace(TopoDS.topods.Face(face)))

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
        results = split_shapes(arguments, tools)

        shapes = []
        for test in results:
            point = compute_shape_centreofmass(test)
            if is_point_behind_plane(point, plane):
                shapes.append(test)
        if shapes:
            if len(shapes) > 1:
                compound = TopoDS.TopoDS_Compound()
                builder = BRep.BRep_Builder()
                builder.MakeCompound(compound)
                for shape in shapes:
                    builder.Add(compound, shape)
                self.occ_shape = compound
            else:
                self.occ_shape = shapes[0]

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
        return OCCBrep.from_native(offset.Shape())
