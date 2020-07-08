import bpy
import bmesh
import mathutils
import itertools
import numpy as np
from datetime import datetime as dt

# Mesh cleaning
Bus_mesh = "Minibus interior"
bus = bpy.data.objects[Bus_mesh]
bpy.ops.object.mode_set(mode="EDIT")
obj = bpy.context.edit_object
me = obj.data
bm = bmesh.from_edit_mesh(me)
viewpoint_distance = 20

top = mathutils.Vector((0, 0, viewpoint_distance))
bottom = mathutils.Vector((0, 0, -viewpoint_distance))
front = mathutils.Vector((viewpoint_distance, 0, 0))
rear = mathutils.Vector((-viewpoint_distance, 0, 0))
left = mathutils.Vector((0, viewpoint_distance, 0))
right = mathutils.Vector((0, -viewpoint_distance, 0))

views_points = [top, bottom, front, rear, left, right]

centroids = []

for f in bm.faces:
    centroids.append(f.calc_center_median())

visible_triangles = []

bpy.ops.object.mode_set(mode="OBJECT")

viewpoints_local = [bus.matrix_world.inverted() @ viewpoint for viewpoint in views_points]

for target in centroids:
    for viewpoint in viewpoints_local:
        ray_direction = (target - viewpoint).normalized()
        hit, loc, norm, face = bus.ray_cast(viewpoint, ray_direction)
        if face not in visible_triangles:
            visible_triangles.append(face)

bpy.ops.object.mode_set(mode="EDIT")
me = obj.data
bm = bmesh.from_edit_mesh(me)
bpy.ops.mesh.select_all(action='DESELECT')
bm.faces.ensure_lookup_table()
for face_ix in visible_triangles:
    bm.faces[face_ix].select = True
    
bmesh.update_edit_mesh(me, True)

# Mesh subdivide
SUBDIVISION_THRESHOLD = 0.0005

bpy.ops.mesh.select_all(action='DESELECT')
biggest_triangle = 0
for f in bm.faces:
    tri_area = f.calc_area()
    if tri_area > SUBDIVISION_THRESHOLD:
        f.select = True
        if tri_area > biggest_triangle:
            biggest_triangle = tri_area

bmesh.update_edit_mesh(me, True)
bpy.ops.mesh.subdivide()
bpy.ops.mesh.select_all(action='DESELECT')
bmesh.ops.triangulate(bm, faces=bm.faces)
bmesh.update_edit_mesh(me, True)
biggest_triangle






