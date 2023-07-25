#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

#include <embree3/rtcore.h>

py::tuple ray_scene_intersection(
        const void* scene_void,
        const py::array_t<float> ray_origins_py,
        const py::array_t<float> ray_directions_py
) {
    RTCScene scene = (RTCScene)scene_void;

    // Recover pointers to arrays.
    py::buffer_info ray_origins_py_buf = ray_origins_py.request();
    float* ray_origins_py_ptr = static_cast<float*>(ray_origins_py_buf.ptr);
    py::buffer_info ray_directions_py_buf = ray_directions_py.request();
    float* ray_directions_py_ptr = static_cast<float*>(ray_directions_py_buf.ptr);

    // Ray.
    assert(ray_origins_py.shape(0) == ray_directions_py.shape(0));
    const int num_rays = ray_origins_py.shape(0);

    // Allocate the output arrays.
    py::array_t<int> geometry_ids_py(
        py::detail::any_container<ssize_t>(
            {num_rays, 2}
        )
    );
    py::buffer_info geometry_ids_py_buf = geometry_ids_py.request();
    int* geometry_ids_py_ptr = static_cast<int*>(geometry_ids_py_buf.ptr);
    py::array_t<float> bcoords_py(
        py::detail::any_container<ssize_t>(
            {num_rays, 2}
        )
    );
    py::buffer_info bcoords_py_buf = bcoords_py.request();
    float* bcoords_py_ptr = static_cast<float*>(bcoords_py_buf.ptr);

    // Ray tracing.
#pragma omp parallel for
    for (int i = 0; i < num_rays; ++i) {
        RTCIntersectContext context;
        rtcInitIntersectContext(&context);
        RTCRayHit ray_hit;
        ray_hit.ray.org_x = ray_origins_py_ptr[i * 3 + 0];
        ray_hit.ray.org_y = ray_origins_py_ptr[i * 3 + 1];
        ray_hit.ray.org_z = ray_origins_py_ptr[i * 3 + 2];
        ray_hit.ray.dir_x = ray_directions_py_ptr[i * 3 + 0];
        ray_hit.ray.dir_y = ray_directions_py_ptr[i * 3 + 1];
        ray_hit.ray.dir_z = ray_directions_py_ptr[i * 3 + 2];
        ray_hit.ray.tnear = 0.0;
        ray_hit.ray.time = 0.0;
        ray_hit.ray.tfar = std::numeric_limits<float>::max();
        ray_hit.ray.id = i;
        ray_hit.hit.geomID = RTC_INVALID_GEOMETRY_ID;
        rtcIntersect1(scene, &context, &ray_hit);
        const unsigned int geometry_id = ray_hit.hit.geomID;
        const unsigned int primitive_id = ray_hit.hit.primID;
        geometry_ids_py_ptr[i * 2 + 0] = geometry_id;
        geometry_ids_py_ptr[i * 2 + 1] = primitive_id;
        const float u = ray_hit.hit.u;
        const float v = ray_hit.hit.v;
        bcoords_py_ptr[i * 2 + 0] = u;
        bcoords_py_ptr[i * 2 + 1] = v;
    }

    return py::make_tuple(geometry_ids_py, bcoords_py);
}
