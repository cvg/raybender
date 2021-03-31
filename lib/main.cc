#include <pybind11/pybind11.h>

namespace py = pybind11;

#include "geometry.cc"
#include "interpolator.cc"
#include "ray.cc"
#include "scene.cc"

PYBIND11_MODULE(_raybender, m) {
    m.doc() = "Ray Tracing bindings";

    // Scene bindings.
    m.def(
        "create_scene", &create_scene,
        py::arg("config") = "frequency_level=simd512",
        "Create an empty scene."
    );
    m.def(
        "release_scene", &release_scene,
        "Release a scene."
    );

    // Geometry bindings.
    m.def(
        "add_triangle_mesh", &add_triangle_mesh,
        "Add triangle mesh to scene."
    );

    // Ray bindings.
    m.def(
        "ray_scene_intersection", &ray_scene_intersection,
        "Intersect ray with scene."
    );

    // Interpolator bindings.
    m.def(
        "barycentric_interpolator", &barycentric_interpolator,
        "Barycentric interpolator."
    );
}
