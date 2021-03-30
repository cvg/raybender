import matplotlib.pyplot as plt

import numpy as np

import open3d as o3d

import os

import raybender as rb

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
        vertex_colors = np.concatenate([np.random.rand(vertices.shape[0], 1), np.zeros([vertices.shape[0], 2])], axis=1).astype(np.float32)
    triangles = np.asarray(mesh.triangles).astype(np.int32)
    del mesh

    # Camera intrinsics.
    # We consider a simple pinhole camera, but arbitrary rays are supported.
    w, h, f, cx, cy = 1920, 1080, 1600.0, 960.0, 540.0

    # Camera extrinsics - world-to-camera.
    R = np.array([0.0750659, 0.0393823, -0.996401, -0.968689, 0.240023, -0.0634912, 0.236658, 0.969968, 0.0561668]).reshape(3, 3)
    tvec = np.array([-53.50685546, -58.21649775, 349.10923205])

    # Ray information.
    num_rays = h * w

    # Ray origins.
    center = - R.T @ tvec
    ray_origins = np.tile(center[np.newaxis, :], (num_rays, 1))

    # Ray directions (one per pixel).
    # x points down and y points right in image.
    x = np.tile(np.arange(w)[np.newaxis, :], (h, 1)).flatten()
    y = np.tile(np.arange(h)[:, np.newaxis], (1, w)).flatten()
    x = (x - cx) / f
    y = (y - cy) / f
    ray_directions = (R.T @ np.stack([x, y, np.ones_like(x)], axis=0)).T

    # Inputs must be contiguous.
    ray_origins = np.ascontiguousarray(ray_origins.astype(np.float32))
    ray_directions = np.ascontiguousarray(ray_directions.astype(np.float32))

    # Create Embree environment.
    t0 = time.time()
    scene = rb.create_scene()
    print("Embree scene creation - %.5fs" % (time.time() - t0))

    # Add mesh to scene.
    t0 = time.time()
    geometry_id = rb.add_triangle_mesh(scene, vertices, triangles)
    print("Adding geometry - %.5fs" % (time.time() - t0))

    # Ray-Scene intersection.
    t0 = time.time()
    geom_ids, bcoords = rb.ray_scene_intersection(scene, ray_origins, ray_directions)
    print('Intersection between ray and scenes - %.5fs' % (time.time() - t0))

    # Filter out rays without intersections.
    valid = (geom_ids[:, 0] != -1)
    tri_ids = geom_ids[:, 1][valid]
    bcoords = bcoords[valid]
    print('Percentage of valid rays - %.2f%%' % (np.mean(valid) * 100))

    # Use barycentric interpolator.
    bcoords = np.ascontiguousarray(bcoords)
    tri_ids = np.ascontiguousarray(tri_ids)
    t0 = time.time()
    locations = rb.barycentric_interpolator(tri_ids, bcoords, triangles, vertices)
    print('Location interpolation - %.5fs' % (time.time() - t0))
    t0 = time.time()
    mesh_colors = rb.barycentric_interpolator(tri_ids, bcoords, triangles, vertex_colors)
    print('Color interpolation - %.5fs' % (time.time() - t0))

    # Compute depth.
    Z = (R @ locations.T)[-1]

    # Populate final arrays.
    depths = np.full(num_rays, np.nan)
    depths[valid] = Z
    colors = np.full([num_rays, 3], 0.0)
    colors[valid] = np.clip(mesh_colors, 0, 1)

    # Plot.
    plt.rc('axes', titlesize=25)
    plt.figure(figsize=[30, 15])
    plt.subplot(1, 2, 1)
    plt.title('Depth')
    plt.imshow(depths.reshape(h, w))
    plt.axis('off')
    plt.subplot(1, 2, 2)
    plt.title ("RGB")
    plt.imshow(colors.reshape(h, w, 3))
    plt.axis('off')
    plt.savefig('rendered.png', dpi=300, bbox_inches='tight')

    # Release environment.
    rb.release_scene(scene)