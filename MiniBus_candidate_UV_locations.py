import bpy
import bmesh
import mathutils
import itertools
import numpy as np
from datetime import datetime as dt

Bus_mesh = "Minibus interior"

# Global variables
Base_area = 0.12485790252685547
UV_range = 2.92608
Lantern_depth = mathutils.Vector((0,0,0.24))
Base_depth = mathutils.Vector((0,0,0.1))


bus = bpy.data.objects[Bus_mesh]
bpy.ops.object.mode_set(mode="EDIT")
obj = bpy.context.edit_object
me = obj.data
bm = bmesh.from_edit_mesh(me)

Total_num_faces = len(bm.faces)
Total_area = 0
for f in bm.faces:
    Total_area += f.calc_area()

Bounding_x_1 = (-4.2, 0.4)
Bounding_y_1 = (-0.8, 0.7)
Bounding_z_1 = (0.8, 1.2)

Bounding_x_2 = (-3.7, -0.3)
Bounding_y_2 = (-0.2, 0.7)
Bounding_z_2 = (0.1, 0.6)

Bounding_x_3 = (-1.8, -0.4)
Bounding_y_3 = (-0.8, -0.25)
Bounding_z_3 = (0.1, 0.6)

Bounding_x_4 = (-0.02, 0.4)
Bounding_y_4 = (-0.8, -0.05)
Bounding_z_4 = (0.1, 0.6)

def Candidate_UV_loc(Bounding_x, Bounding_y, Bounding_z, x, y, z):
    candidate_x = np.linspace(Bounding_x[0], Bounding_x[1], x)
    candidate_y = np.linspace(Bounding_y[0], Bounding_y[1], y)
    candidate_z = np.linspace(Bounding_z[0], Bounding_z[1], z)
    candidate_loc = [mathutils.Vector(i) for i in itertools.product(candidate_x, candidate_y, candidate_z)]
    return(candidate_loc)

def Candidate_UV_visulizer(candidate_loc):
    ob = bpy.data.objects.get("Cylinder")
    for loc in candidate_loc:
        ob_dup = ob.copy()
        ob_dup.location = loc
        bpy.data.collections['Candidate_UV_loc'].objects.link(ob_dup)

def Remove_collection(collection):
    for c in bpy.context.scene.collection.children:
        if c.name == collection:
            bpy.context.scene.collection.children.unlink(c)

candidate_loc_1 = Candidate_UV_loc(Bounding_x_1, Bounding_y_1, Bounding_z_1, 12, 5, 3)
candidate_loc_2 = Candidate_UV_loc(Bounding_x_2, Bounding_y_2, Bounding_z_2, 9, 3, 4)
candidate_loc_3 = Candidate_UV_loc(Bounding_x_3, Bounding_y_3, Bounding_z_3, 3, 2, 4)
candidate_loc_4 = Candidate_UV_loc(Bounding_x_4, Bounding_y_4, Bounding_z_4, 2, 3, 4)
candidate_loc = candidate_loc_1 + candidate_loc_2 + candidate_loc_3 + candidate_loc_4

# Create a collection to visualize candidate lantern locations
Candidate_UV_loc = bpy.data.collections.new("Candidate_UV_loc")
bpy.context.scene.collection.children.link(Candidate_UV_loc)
Candidate_UV_visulizer(candidate_loc)

# Remove_collection('Candidate_UV_loc')



