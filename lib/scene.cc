#include <embree3/rtcore.h>

void* create_scene(std::string config) {
    RTCDevice device = rtcNewDevice(config.c_str());
    RTCScene scene = rtcNewScene(device);
    // Avoid optimizations that lower the arithmetic accuracy.
    // Solves most problems with rays passing through edges / vertices.
    rtcSetSceneFlags(scene, RTC_SCENE_FLAG_ROBUST);
    return (void*)scene;
}

void release_scene(void* scene_void) {
    RTCScene scene = (RTCScene)scene_void;
    RTCDevice device = rtcGetSceneDevice(scene);
    // This releases all geometries part of the scene too.
    rtcReleaseScene(scene);
    rtcReleaseDevice(device);
}
