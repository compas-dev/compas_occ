from compas.geometry import (
    Point,
    Vector,
    Line
)

from OCC.Core.gp import (
    gp_Pnt,
    gp_Vec,
    gp_Dir,
    gp_Lin
)


def compas_point_to_occ_point(self: Point) -> gp_Pnt:
    return gp_Pnt(* self)


def compas_point_from_occ_point(cls: Point, point: gp_Pnt) -> Point:
    return cls(point.X(), point.Y(), point.Z())


def compas_vector_to_occ_vector(self: Vector) -> gp_Vec:
    return gp_Vec(* self)


def compas_vector_from_occ_vector(cls: Vector, vector: gp_Vec) -> Vector:
    return cls(vector.X(), vector.Y(), vector.Z())


def compas_vector_to_occ_direction(self: Vector) -> gp_Dir:
    return gp_Dir(* self)


def compas_line_to_occ_line(self: Line) -> gp_Lin:
    return gp_Lin(self.start.to_occ_point(), self.direction.to_occ_direction())
