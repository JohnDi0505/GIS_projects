import bpy
import bmesh
import mathutils
import itertools
import numpy as np
from datetime import datetime as dt

# Global variables
Bus_mesh = "Bus Interior"


Total_area = 193.28846836844235
Base_area = 0.12485790252685547
UV_range = 2.92608
Lantern_depth = mathutils.Vector((0,0,0.3556))
Base_depth = mathutils.Vector((0,0,0.1))
Base_radius = 0.127

Bounding_x = (-2.28, 0)
Bounding_y = (-5.6,5.6)
Bounding_z = (-1.44, 1.44)

bus = bpy.data.objects[Bus_mesh]
bpy.ops.object.mode_set(mode="EDIT")
obj = bpy.context.edit_object
me = obj.data
bm = bmesh.from_edit_mesh(me)
Total_num_faces = len(bm.faces)

centroids = []
for f in bm.faces:
    centroids.append(f.calc_center_median())

UV = mathutils.Vector((-1.28, 0, 1))

def UV(loc):
    base = loc + Lantern_depth
    upper_end = loc + Lantern_depth - Base_depth / 2 - mathutils.Vector((0, 0, 0.01))
    lower_end = loc - Lantern_depth
    return(upper_end, lower_end, base)

bpy.ops.mesh.primitive_cylinder_add(radius = Base_radius, depth = Base_depth.z, location = UV1[2] + Lantern_depth)
bpy.ops.mesh.select_all(action='DESELECT')
base = bm.faces[Total_num_faces:]
bmesh.ops.delete(bm, geom=base, context='FACES')
bmesh.update_edit_mesh(me, True)

visible_triangles = []
    # Must switch to OBJECT mode before using raycasting
bpy.ops.object.mode_set(mode="OBJECT")
    # Convert world coordinate system to local (bus)
light_sources = [bus.matrix_world.inverted() @ world_loc for world_loc in UV_loc_config]

for target in centroids:
    for UV_source in light_sources:
        ray_direction = (target - UV_source).normalized()
        if ray_direction.length < UV_range:
            hit, loc, norm, face = bus.ray_cast(UV_source, ray_direction)
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







# Create a collection to visualize candidate lantern locations
Candidate_UV_loc = bpy.data.collections.new("Candidate_UV_loc")
bpy.context.scene.collection.children.link(Candidate_UV_loc)

def Candidate_UV_loc(x, y, z):
    candidate_x = np.linspace(Bounding_x[0] + 0.5, Bounding_x[1] - 0.5, x)
    candidate_y = np.linspace(Bounding_y[0] + 0.8, Bounding_y[1] - 0.5, y)
    candidate_z = np.linspace(0.85762, 1.06985, z)
    candidate_loc = [mathutils.Vector(i) for i in itertools.product(candidate_x, candidate_y, candidate_z)]
    
    return(candidate_loc)

def Candidate_UV_visulizer(candidate_loc):
    ob = bpy.data.objects.get("Cylinder")
    for loc in candidate_loc:
        ob_dup = ob.copy()
        ob_dup.location = loc
        bpy.data.collections['Candidate_UV_loc'].objects.link(ob_dup)


for collection in bpy.data.collections:
    print(collection.name)
    for obj in collection.all_objects:
        print(obj.name)


# Remove a collection
for c in bpy.context.scene.collection.children:
     if c.name == "Candidate_UV_loc":
         bpy.context.scene.collection.children.unlink(c)
