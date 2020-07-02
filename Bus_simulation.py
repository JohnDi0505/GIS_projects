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
bpy.ops.import_mesh.stl(filepath="C://Bus_UV_simulation//bus.stl")
bus = bpy.data.objects['Bus']
bus = bpy.data.objects['Bus_interior']

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



## declare external view points
#viewpoint_distance = 10

#top = mathutils.Vector((0, 0, viewpoint_distance))
#bottom = mathutils.Vector((0, 0, -viewpoint_distance))
#front = mathutils.Vector((viewpoint_distance, 0, 0))
#rear = mathutils.Vector((-viewpoint_distance, 0, 0))
#left = mathutils.Vector((0, viewpoint_distance, 0))
#right = mathutils.Vector((0, -viewpoint_distance, 0))

#viewpoints = [top, bottom, front, rear, left, right]

## raycast from outside viewpoints
#bpy.ops.object.mode_set(mode="EDIT")
#obj = bpy.context.edit_object
#me = obj.data
#bm = bmesh.from_edit_mesh(me)

#centroids = []

#for f in bm.faces:
#    centroids.append(f.calc_center_median())

## perform raycast under "OBJECT" mode
#visible_triangles = []

#bpy.ops.object.mode_set(mode="OBJECT")

#viewpoints_local = [bus.matrix_world.inverted() @ viewpoint for viewpoint in viewpoints]

#for target in centroids:
#    for viewpoint in viewpoints_local:
#        ray_direction = (target - viewpoint).normalized()
#        hit, loc, norm, face = bus.ray_cast(viewpoint, ray_direction)
#        if face not in visible_triangles:
#            visible_triangles.append(face)
#        
## visualize visible triangles
#bpy.ops.object.mode_set(mode="EDIT")
#me = obj.data
#bm = bmesh.from_edit_mesh(me)

#bpy.ops.mesh.select_all(action='DESELECT')
#bm.faces.ensure_lookup_table()
#for face_ix in visible_triangles:
#    bm.faces[face_ix].select = True
#    
#bmesh.update_edit_mesh(me, True)

#f = open("internal_triangles.txt", 'w')

#for face in bm.faces:
#    f.write("%d\n" % (face.index))
#    
#f.close()



# subdivide faces to below 1 square centimeter

SUBDIVISION_THRESHOLD = 0.01 # square meter (1 square centimeter)

bpy.ops.object.mode_set(mode="EDIT")

obj = bpy.context.edit_object
me = obj.data
bm = bmesh.from_edit_mesh(me)

#bpy.ops.mesh.select_all(action='DESELECT')

total_num_faces = len(bm.faces)

for f in bm.faces:
    area_ratio = f.calc_area() / SUBDIVISION_THRESHOLD
    if area_ratio > 1:
        num_of_cuts = ceil(sqrt(area_ratio))
        bmesh.ops.subdivide_edges(bm, edges=f.edges, cuts=num_of_cuts, use_grid_fill=True)

bmesh.update_edit_mesh(me, True)


bpy.ops.mesh.select_all(action='DESELECT')

for f in bm.faces:
    if f.calc_area() > SUBDIVISION_THRESHOLD:
        f.select = True
        
bmesh.update_edit_mesh(me, True)

bpy.ops.mesh.subdivide(number_cuts=1)

# directly subdivide meshes
#bpy.ops.mesh.subdivide(number_cuts=1)



# Total internal area 193.28846836844235 square meter


# add a cylindrical base to the scene
Lantern_depth = 0.12
UV1 = mathutils.Vector((-1.14605, 2.0269, 1.0698))
UV1_base = mathutils.Vector((-1.14605, 2.0269, 1.0698 + Lantern_depth))
UV2 = mathutils.Vector((-1.14605, -1.63068, 1.0698))
UV2_base = mathutils.Vector((-1.14605, -1.63068, 1.0698 + Lantern_depth))

bpy.ops.mesh.primitive_cylinder_add(radius = 0.2, depth = 0.05, location = UV1_base)
# get the indices of all faces on the cylinder
base1_ix = [f.index for f in bm.faces if f.select == True]
bpy.ops.mesh.select_all(action='DESELECT')

bpy.ops.mesh.primitive_cylinder_add(radius = 0.2, depth = 0.05, location = UV2_base)
# get the indices of all faces on the cylinder
base2_ix = [f.index for f in bm.faces if f.select == True]
bpy.ops.mesh.select_all(action='DESELECT')

# to remove the base from the scene
base = [bm.faces[i] for i in base2_ix]
# delete bases after completing raycast
bmesh.ops.delete(bm, geom=base, context='FACES')
bmesh.update_edit_mesh(me, True)

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


# dual UV light raycasting
visible_triangles = []

bpy.ops.object.mode_set(mode="OBJECT")

UV_position_1 = bpy.data.objects['UV1'].location
UV_position_local_1 = bus.matrix_world.inverted() @ UV_position_1

UV_position_2 = bpy.data.objects['UV2'].location
UV_position_local_2 = bus.matrix_world.inverted() @ UV_position_2

for target in centroids:
    ray_direction_1 = (target - UV_position_1).normalized()
    ray_direction_2 = (target - UV_position_2).normalized()
    hit1, loc1, norm1, face1 = bus.ray_cast(UV_position_local_1, ray_direction_1)
    hit2, loc2, norm2, face2 = bus.ray_cast(UV_position_local_2, ray_direction_2)
    if face1 not in visible_triangles:
        visible_triangles.append(face1)
    if face2 not in visible_triangles:
        visible_triangles.append(face2)
        
# visualize visible triangles
bpy.ops.object.mode_set(mode="EDIT")
me = obj.data
bm = bmesh.from_edit_mesh(me)

bpy.ops.mesh.select_all(action='DESELECT')
bm.faces.ensure_lookup_table()
for face_ix in visible_triangles:
    bm.faces[face_ix].select = True
    
bmesh.update_edit_mesh(me, True)