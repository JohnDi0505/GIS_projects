# GIS_projects
scripts for GIS projects

#Project 1: VR LIDAR Data
stage 1 (done): Load LIDAR point clouds to Python with "laspy" library --> construct array using numpy to accommodate X,Y,Z information &
value normalization using scale function in sklearn.preprocessing library --> 3D visualization using pptk library --> compile objects for
vertices & faces to output .ply file --> load .ply file in blender

stage 2 (in progress): 1. identify objects (i.e. ground point, tree, rock) from point cloud attributes & differentiate objects by color;
2. literature review to compare working with LIDAR data in the field & metropolitan area; 3. literature review to identify tools to render
point clouds (overlay 2D NAIP image on 3D model? or render point clouds using texture in blender & UE4?)

stage 3 (in future): VR application development
