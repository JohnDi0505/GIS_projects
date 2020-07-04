import bpy
import bmesh
import mathutils
import itertools
import numpy as np
import datetime as dt

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
Candidate_loc_4_lanterns = {'UV1':[(-1.85682, 5.33904, 0.79430),
                                   (-1.85682, 4.56417, 0.79430),
                                   (-1.14968, 4.99024, 1.06985),
                                   (-0.50650, 5.33904, 0.91426),
                                   (-0.50650, 4.59515, 0.91426)],
                            'UV2':[(-1.14968, 3.49667, 1.06985),
                                   (-1.79252, 3.49667, 0.85762),
                                   (-0.68847, 3.49667, 0.85762),
                                   (-0.68847, 2.83945, 0.85762),
                                   (-1.81653, 2.83945, 0.85762),
                                   (-1.14968, 2.83945, 1.06985)],
                            'UV3':[(-1.14968, 1.20881, 1.06985),
                                   (-1.90625, 1.20881, 0.85762),
                                   (-0.68847, 1.20881, 0.85762),
                                   (-1.14968, -0.42995,1.06985),
                                   (-1.81653, -0.42995,0.85762),
                                   (-1.14968, -1.64538,1.06985),
                                   (-0.68847, -1.64538,0.85762),
                                   (-1.81653, -1.64538,0.85762)],
                            'UV4':[(-1.14968, -2.84190,1.06985),
                                   (-1.81653, -2.84190,0.85762),
                                   (-0.68847, -2.84190,0.85762),
                                   (-1.14968, -4.13961,1.06985),
                                   (-1.81653, -4.13961,0.85762),
                                   (-0.68847, -4.13961,0.85762)]}

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







# Parse results to csv file
def result_to_csv(summary):
    # Add a timestamp to the output file
    year = str(dt.datetime.now().year)
    month = str(dt.datetime.now().month)
    day = str(dt.datetime.now().day)
    hour = str(dt.datetime.now().hour)
    minute = str(dt.datetime.now().minute)
    second = str(dt.datetime.now().second)
    timestamp = year + month + day + hour + minute + second 
    header = ['index', 'UV1_x', 'UV1_y', 'UV1_z', 'UV2_x', 'UV2_y', 'UV2_z','UV3_x', 'UV3_y', 'UV3_z', 'coverage']
    # Creating output csv file
    f = open('%d_lantern_config_%s.csv' % (len(summary[0]['co']), timestamp), 'w')
    # Writing csv header
    for tx in header:
        f.write("%s," % (tx))
    f.write("\n")
    # Writing data
    for i in summary.keys():
        f.write("%d," % (i))
        for pt in summary[i]['co']:
            for co in list(pt):
                f.write("%.4f," % (co))
        f.write("%.4f\n" % (summary[i]['coverage']))
    f.close()
