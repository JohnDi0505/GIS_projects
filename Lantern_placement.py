import bpy
import bmesh
import mathutils
import itertools
import numpy as np

# Global variables
Bus_mesh = "Bus_interior"

Total_num_faces = 99220
Total_area = 193.28846836844235
Base_area = 0.12485790252685547
Lantern_depth = mathutils.Vector((0,0,0.12))

Candidate_loc_3_lanterns = {'UV1':[(-1.14968, 4.99024, 1.06985),
                                   (-1.14968, 4.14883, 1.06985),
                                   (-1.14968, 3.20375, 1.06985)],
                            'UV2':[(-1.14968, 2.08084,1.06985),
                                   (-1.14968, 0.92232,1.06985),
                                   (-1.14968, -0.42995,1.06985)],
                            'UV3':[(-1.14968, -1.87164,1.06985),
                                   (-1.14968, -2.83522,1.06985),
                                   (-1.14968, -4.65756,1.06985)]}
Candidate_loc_4_lanterns = {'UV1':[], 'UV2':[], 'UV3':[], 'UV4':[]}

# Handle candidate UV location
def UV_loc(candidate_UV_loc):
    n = 0
    summary = {}
    for placement in itertools.product(*[candidate_UV_loc[UV_co] for UV_co in candidate_UV_loc.keys()]):
        summary[n] = {'co': [mathutils.Vector(UV) for UV in placement],'coverage':0}
        n += 1
    return(summary)

def UV_placement_visualizer(UV_loc_config):
    marker_height = mathutils.Vector((0, 0, 5))
    for i in np.arange(len(UV_loc_config)):
        # place lantern to specified location in blender scene
        bpy.data.objects['UV%d' % (i + 1)].location = UV_loc_config[i]
        # place lantern markers to corresponding locations
        bpy.data.objects['UV%d_marker' % (i + 1)].location = UV_loc_config[i] + marker_height

def UV_Coverage(UV_loc_config):
    # Clear all selections in OBJECT mode & select bus mesh
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['Bus_interior'].select_set(True)
    # Add lantern base meshes under EDIT mode
    bus = bpy.data.objects[Bus_mesh]
    bpy.ops.object.mode_set(mode="EDIT")
    obj = bpy.context.edit_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    mesh_face_num = len(bm.faces)
    # Compute centroids for all triangles in the mesh
    centroids = []
    for f in bm.faces:
        centroids.append(f.calc_center_median())
    # Create UV lantern bases
    for UV_loc in UV_loc_config:
        bpy.ops.mesh.primitive_cylinder_add(radius = 0.2, depth = 0.05, location = UV_loc + Lantern_depth)
    bpy.ops.mesh.select_all(action='DESELECT')
    # Computing visible triangles
    visible_triangles = []
    # Must switch to OBJECT mode before using raycasting
    bpy.ops.object.mode_set(mode="OBJECT")
    # Convert world coordinate system to local (bus)
    light_sources = [bus.matrix_world.inverted() @ world_loc for world_loc in UV_loc_config]
    # Raycasting
    for target in centroids:
        for UV_source in light_sources:
            ray_direction = (target - UV_source).normalized()
            hit, loc, norm, face = bus.ray_cast(UV_source, ray_direction)
            if face not in visible_triangles:
                visible_triangles.append(face)
    # Select visible triangles
    bpy.ops.object.mode_set(mode="EDIT")
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    bpy.ops.mesh.select_all(action='DESELECT')
    bm.faces.ensure_lookup_table()
    for face_ix in visible_triangles:
        bm.faces[face_ix].select = True
    bmesh.update_edit_mesh(me, True)
    # Computing coverage
    Area = 0
    for f in bm.faces:
        if f.select:
            Area += f.calc_area()
    Coverage = (Area - 3 * Base_area) / Total_area
    # Remove UV lantern bases after computing coverage
    bpy.ops.mesh.select_all(action='DESELECT')
    base = bm.faces[mesh_face_num:]
    bmesh.ops.delete(bm, geom=base, context='FACES')
    bmesh.update_edit_mesh(me, True)
    bpy.ops.object.mode_set(mode="OBJECT")
    return(Coverage)
        
# Batch to compute lantern coverage
def Batch_Coverage(summary):
    for placement_config_ix in summary.keys():
        summary[placement_config_ix]['coverage'] = UV_Coverage(summary[placement_config_ix]['co'])
