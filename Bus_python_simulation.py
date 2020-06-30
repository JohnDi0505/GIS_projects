import bpy
import bmesh
import mathutils
import numpy as np

# select "Camera" & "Cube" objects and delect them from the default scene
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects['Camera'].select_set(True)
bpy.ops.object.delete()

bpy.data.objects['Cube'].select_set(True)
bpy.ops.object.delete()

# import the bus model into blender
bpy.ops.import_mesh.stl(filepath="C://Users//RISE-Alienware2//Documents//UVC Simulation//bus.stl")
bus = bpy.data.objects['Bus']

# check the dimensions of the mesh
bpy.data.objects['Bus'].dimensions.x            # 2.56
bpy.data.objects['Bus'].dimensions.y            # 11.25
bpy.data.objects['Bus'].dimensions.z            # 2.90

# enter edit mode
bpy.ops.object.mode_set(mode="EDIT")

obj = bpy.context.edit_object
me = obj.data
bm = bmesh.from_edit_mesh(me)

# Use "bm.faces[face index].verts[vertices index].co" to access the coordinates of vertices

for f in bm.faces:
    if f.select:
        print(f.index)

# Show the updates in the viewport
# and recalculate n-gon tessellation.
bmesh.update_edit_mesh(me, True)

# set cursor location
bpy.context.scene.cursor.location = (0, 0, 0)









# get centroids from all triangles under "EDIT" mode
bpy.ops.object.mode_set(mode="EDIT")
obj = bpy.context.edit_object
me = obj.data
bm = bmesh.from_edit_mesh(me)

centroids = []

for f in bm.faces:
    centroids.append(f.calc_center_median())

# perform raycast under "OBJECT" mode
visible_triangles = []

bpy.ops.object.mode_set(mode="OBJECT")

UV_position = bpy.data.objects['UV'].location
UV_position_local = bus.matrix_world.inverted() @ UV_position

for target in centroids:
    ray_direction = (target - UV_position).normalized()
    hit, loc, norm, face = bus.ray_cast(UV_position_local, ray_direction)
    if face not in visible_triangles:
        visible_triangles.append(face)
        
# visualize visible triangles
bpy.ops.object.mode_set(mode="EDIT")
me = obj.data
bm = bmesh.from_edit_mesh(me)

bpy.ops.mesh.select_all(action='DESELECT')
bm.faces.ensure_lookup_table()
for face_ix in visible_triangles:
    bm.faces[face_ix].select = True
    
bmesh.update_edit_mesh(me, True)