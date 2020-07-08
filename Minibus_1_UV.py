import bpy
import bmesh
import mathutils
import itertools
import numpy as np
from datetime import datetime as dt

# Global variables
Bus_mesh = "Minibus interior"
UV_range = 2.92608
Lantern_depth = mathutils.Vector((0,0,0.2))
Base_depth = mathutils.Vector((0,0,0.1))
Base_radius = 0.127

# Read candidate locations file
f_in = open("candidate_loc.csv", 'r')
candidate_loc = [mathutils.Vector([float(co) for co in line.rstrip().split(',')]) for line in f_in.readlines()]
f_in.close()

bus = bpy.data.objects[Bus_mesh]
bpy.ops.object.mode_set(mode="EDIT")
obj = bpy.context.edit_object
me = obj.data
bm = bmesh.from_edit_mesh(me)
Total_num_faces = len(bm.faces)
Total_area = 0

for f in bm.faces:
    Total_area += f.calc_area()

centroids = []
for f in bm.faces:
    centroids.append(f.calc_center_median())

def UV(loc):
    base = loc + Lantern_depth / 2
    upper_end = loc + Lantern_depth / 2 - Base_depth / 2 - mathutils.Vector((0, 0, 0.01))
    lower_end = loc - Lantern_depth / 2
    return(upper_end, lower_end, base)

def calc_coverage(UV_loc_list):
    bpy.ops.mesh.select_all(action='DESELECT')
    lantern_sources = []
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(me)
    for uv in UV_loc_list:
        temp = list(UV(uv))
        lantern_sources += temp[:2]
        bpy.ops.mesh.primitive_cylinder_add(radius = Base_radius, depth = Base_depth.z, location = temp[2])
    bpy.ops.mesh.select_all(action='DESELECT')
    visible_triangles = []
    # Must switch to OBJECT mode before using raycasting
    bpy.ops.object.mode_set(mode="OBJECT")
    # Convert world coordinate system to local (bus)
    light_sources = [bus.matrix_world.inverted() @ world_loc for world_loc in lantern_sources]
    for target in centroids:
        for UV_source in light_sources:
            ray_direction = (target - UV_source).normalized()
            if ray_direction.length < UV_range:
                hit, loc, norm, face = bus.ray_cast(UV_source, ray_direction)
                if face not in visible_triangles:
                    visible_triangles.append(face)
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(me)
    bpy.ops.mesh.select_all(action='DESELECT')
    bm.faces.ensure_lookup_table()
    for face_ix in visible_triangles:
        bm.faces[face_ix].select = True
    base = bm.faces[Total_num_faces:]
    bmesh.ops.delete(bm, geom=base, context='FACES')
    bmesh.update_edit_mesh(me, True)
    Area = 0
    for f in bm.faces:
        if f.select:
            Area += f.calc_area()
    coverage = Area / Total_area
    return(coverage)
    
for UV_loc_entry in np.arange(len(candidate_loc)):
    
