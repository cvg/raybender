
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

#include <embree3/rtcore.h>

#include <iostream>

struct Triangle {
    int v0, v1, v2;
};

struct Vec3f {
    float x, y, z;
};

unsigned int add_triangle_mesh(
        const void* scene_void,
        const py::array_t<float> vertices_py,
        const py::array_t<int> triangles_py
) {
    RTCScene scene = (RTCScene)scene_void;
    RTCDevice device = rtcGetSceneDevice(scene);
    RTCGeometry mesh = rtcNewGeometry(device, RTC_GEOMETRY_TYPE_TRIANGLE);
 
    // Recover pointers to arrays.
    py::buffer_info vertices_py_buf = vertices_py.request();
    float* vertices_py_ptr = static_cast<float*>(vertices_py_buf.ptr);
    py::buffer_info triangles_py_buf = triangles_py.request();
    int* triangles_py_ptr = static_cast<int*>(triangles_py_buf.ptr);

    // Create vertices.
    assert(vertices_py.shape(0) == vertex_colors_py.shape(0));
    const int num_vertices = vertices_py.shape(0);
    Vec3f* vertices = (Vec3f*)rtcSetNewGeometryBuffer(mesh, RTC_BUFFER_TYPE_VERTEX, 0, RTC_FORMAT_FLOAT3, sizeof(Vec3f), num_vertices);
#pragma omp parallel for
    for (int i = 0; i < num_vertices; ++i) {
        vertices[i].x = vertices_py_ptr[i * 3 + 0];
        vertices[i].y = vertices_py_ptr[i * 3 + 1];
        vertices[i].z = vertices_py_ptr[i * 3 + 2];
    }

    // Create triangles.
    const int num_triangles = triangles_py.shape(0);
    Triangle* triangles = (Triangle*)rtcSetNewGeometryBuffer(mesh, RTC_BUFFER_TYPE_INDEX, 0, RTC_FORMAT_UINT3, sizeof(Triangle), num_triangles);
#pragma omp parallel for
    for (int i = 0; i < num_triangles; ++i) {
        triangles[i].v0 = triangles_py_ptr[i * 3 + 0];
        triangles[i].v1 = triangles_py_ptr[i * 3 + 1];
        triangles[i].v2 = triangles_py_ptr[i * 3 + 2];
    }

    // Attach geometry.
    rtcCommitGeometry(mesh);
    const unsigned int geometry_id = rtcAttachGeometry(scene, mesh);
    rtcReleaseGeometry(mesh);
    rtcCommitScene(scene);
    return geometry_id;
}
