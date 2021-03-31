def compute_rays_for_simple_pinhole_camera(R, tvec, intrinsics):
    import numpy as np

    # Recover intrinsics.
    w, h, f, cx, cy = intrinsics

    # Number of rays.
    num_rays = h * w

    # Ray origins (same for all pixels).
    center = - R.T @ tvec
    origins = np.tile(center[np.newaxis, :], (num_rays, 1))

    # Ray directions (one per pixel).
    # x points down and y points right in image.
    x = np.tile(np.arange(w)[np.newaxis, :], (h, 1)).flatten()
    y = np.tile(np.arange(h)[:, np.newaxis], (1, w)).flatten()
    x = (x - cx) / f
    y = (y - cy) / f
    directions = (R.T @ np.stack([x, y, np.ones_like(x)], axis=0)).T

    # Outputs must be contiguous.
    origins = np.ascontiguousarray(origins.astype(np.float32))
    directions = np.ascontiguousarray(directions.astype(np.float32))

    return origins, directions


def filter_intersections(geom_ids, bcoords):
    import numpy as np

    # Geometry id is -1 if ray doesn't interesect any mesh.
    valid = (geom_ids[:, 0] != -1)
    gids = geom_ids[:, 0][valid]
    tids = geom_ids[:, 1][valid]
    bcoords = bcoords[valid]
    
    # Outputs must be contiguous.
    gids = np.ascontiguousarray(gids)
    tids = np.ascontiguousarray(tids)
    bcoords = np.ascontiguousarray(bcoords)

    return gids, tids, bcoords, valid


def interpolate_rgbd_from_geometry(triangles, vertices, vertex_colors, tri_ids, bcoords, valid, R, w, h):
    import numpy as np

    from ._raybender import barycentric_interpolator

    # Number of rays.
    num_rays = h * w

    # Interpolate RGB.
    if vertex_colors is None:
        rgb = np.full(num_rays * 3, 0)
    else:
        # Compute ray hit colors.
        mesh_rgb = barycentric_interpolator(tri_ids, bcoords, triangles, vertex_colors)
       
        # Populate final array.
        rgb = np.full([num_rays, 3], 0)
        rgb[valid] = np.clip(mesh_rgb, 0, 1)
    
    # Interpolate depth.
    if vertices is None:
        depth = np.full(num_rays, np.nan)
    else:
        # Compute ray hit locations.
        locations = barycentric_interpolator(tri_ids, bcoords, triangles, vertices)

        # Compute depth.
        Z = (R @ locations.T)[-1]
        
        # Populate final array.
        depth = np.full(num_rays, np.nan)
        depth[valid] = Z

    # Reshape arrays.
    rgb = rgb.reshape(h, w, 3)
    depth = depth.reshape(h, w)

    return rgb, depth
