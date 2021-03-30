#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

py::array_t<float> barycentric_interpolator(
        const py::array_t<int> triangle_ids_py,
        const py::array_t<float> bcoords_py,
        const py::array_t<int> triangles_py,
        const py::array_t<float> values_py
) { 
    // Recover pointers to arrays.
    py::buffer_info triangle_ids_py_buf = triangle_ids_py.request();
    int* triangle_ids_py_ptr = static_cast<int*>(triangle_ids_py_buf.ptr);
    py::buffer_info bcoords_py_buf = bcoords_py.request();
    float* bcoords_py_ptr = static_cast<float*>(bcoords_py_buf.ptr);
    py::buffer_info triangles_py_buf = triangles_py.request();
    int* triangles_py_ptr = static_cast<int*>(triangles_py_buf.ptr);
    py::buffer_info values_py_buf = values_py.request();
    float* values_py_ptr = static_cast<float*>(values_py_buf.ptr);

    // Allocate the output arrays.
    const int num_rays = bcoords_py.shape(0);
    const int dims = values_py.shape(1);
    py::array_t<float> interpolated_values_py(
        py::detail::any_container<ssize_t>(
            {num_rays, dims}
        )
    );
    py::buffer_info interpolated_values_py_buf = interpolated_values_py.request();
    float* interpolated_values_py_ptr = static_cast<float*>(interpolated_values_py_buf.ptr);

    // Look into using the Embree interpolator which requires aligned structures Val3fa - rtcInterpolate.
    // Main loop.
#pragma omp parallel for
    for (int i = 0; i < num_rays; ++i) {
        const int triangle_id = triangle_ids_py_ptr[i];
        const float u = bcoords_py_ptr[i * 2 + 0];
        const float v = bcoords_py_ptr[i * 2 + 1];
        const int vertex_id0 = triangles_py_ptr[triangle_id * 3 + 0];
        const int vertex_id1 = triangles_py_ptr[triangle_id * 3 + 1];
        const int vertex_id2 = triangles_py_ptr[triangle_id * 3 + 2];
        for (int j = 0; j < dims; ++j) {
            const float vertex_val0 = values_py_ptr[vertex_id0 * dims + j];
            const float vertex_val1 = values_py_ptr[vertex_id1 * dims + j];
            const float vertex_val2 = values_py_ptr[vertex_id2 * dims + j];
            interpolated_values_py_ptr[i * dims + j] = (1 - u - v) * vertex_val0 + u * vertex_val1 + v * vertex_val2;
        }
    }

    return interpolated_values_py;
}