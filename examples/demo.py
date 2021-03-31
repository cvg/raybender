import matplotlib.pyplot as plt

import numpy as np

import open3d as o3d

import os

import PIL

import raybender as rb
import raybender.utils as rbutils

import time

import urllib
import urllib.request as urlrequest


if __name__ == '__main__':
    # Load mesh.
    mesh_url = 'https://github.com/seminar2012/Open3D/blob/master/examples/TestData/knot.ply?raw=true'
    request = urlrequest.urlopen(mesh_url)
    content = request.read()
    with open('mesh.ply', 'wb') as file:
        file.write(content)
    mesh = o3d.io.read_triangle_mesh('mesh.ply')
    os.remove('mesh.ply')

    # Recover data from mesh.
    vertices = np.asarray(mesh.vertices).astype(np.float32)
    if mesh.has_vertex_colors():
        vertex_colors = np.asarray(mesh.vertex_colors).astype(np.float32)
    else:
        vertex_colors = np.random.rand(vertices.shape[0], 3).astype(np.float32)
    triangles = np.asarray(mesh.triangles).astype(np.int32)
    del mesh

    # Camera intrinsics.
    # We consider a simple pinhole camera, but arbitrary rays are supported.
    # w, h, f, cx, cy
    intrinsics = [1920, 1080, 1600.0, 960.0, 540.0]
    w, h = intrinsics[: 2]

    # Camera extrinsics in world-to-camera convention.
    # X_cam = R * X_world + tvec
    R = np.array([0.0750659, 0.0393823, -0.996401, -0.968689, 0.240023, -0.0634912, 0.236658, 0.969968, 0.0561668]).reshape(3, 3)
    tvec = np.array([-53.50685546, -58.21649775, 349.10923205])

    # Ray information.
    ray_origins, ray_directions = rbutils.compute_rays_for_simple_pinhole_camera(R, tvec, intrinsics)

    # Create Embree environment.
    t0 = time.time()
    scene = rb.create_scene()
    print("Embree scene creation - %.5fs" % (time.time() - t0))

    # Add mesh to scene.
    t0 = time.time()
    geometry_id = rb.add_triangle_mesh(scene, vertices, triangles)
    print("Adding geometry - %.5fs" % (time.time() - t0))

    # Intersect rays with scene.
    t0 = time.time()
    geom_ids, bcoords = rb.ray_scene_intersection(scene, ray_origins, ray_directions)
    print('Intersection between ray and scenes - %.5fs' % (time.time() - t0))

    # Filter out rays without intersections.
    geom_ids, tri_ids, bcoords, valid = rbutils.filter_intersections(geom_ids, bcoords)
    print('Percentage of valid rays - %.2f%%' % (geom_ids.shape[0] / ray_origins.shape[0] * 100))

    # Use barycentric interpolator to recover depth and RGB.
    t0 = time.time()
    # Interpolators should be called once for each mesh (geom_id) with its associated ray intersections.
    # In this case, we have a single mesh. Please refer to interpolate_rgbd_from_geometry for more details.
    rgb, depth = rbutils.interpolate_rgbd_from_geometry(triangles, vertices, vertex_colors, tri_ids, bcoords, valid, R, w, h)
    print('Interpolation - %.5fs' % (time.time() - t0))

    # Save image and depth.
    im = PIL.Image.fromarray((rgb * 255).astype(np.uint8))
    im.save('rgb.png')
    np.save('depth.npy', depth)

    # Plot.
    plt.rc('axes', titlesize=25)
    plt.figure(figsize=[30, 15])
    plt.subplot(1, 2, 1)
    plt.title ("RGB")
    plt.imshow(rgb)
    plt.axis('off')
    plt.subplot(1, 2, 2)
    plt.title('Depth')
    plt.imshow(depth)
    plt.axis('off')
    plt.savefig('plot.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Release environment.
    rb.release_scene(scene)