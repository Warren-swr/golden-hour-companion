"""Build the v3 scene: reviewed v2 scene + model polish + new camera choreography."""
import json
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
sys.path.insert(0, str(HERE))
import polish_models
import cinematography


def main():
    bpy.ops.wm.open_mainfile(filepath=str(OUT / 'source' / 'v2_reviewed_scene.blend'))
    polish = polish_models.main()
    cinematography.build()
    sc = bpy.context.scene
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = .5
    sc['production_revision'] = 'forest_retreat_v3 / model polish and six-shot cinematic camera language'
    sc['render_contract'] = 'Native 2160 square, 24 fps, 1056 source frames, 44 seconds, 6 arc-length camera moves'
    sc['animation'] = ('Six shots: reference hold and pull-back, kitchen slider, bedroom arc, threshold oner, '
                       'waterline slider, crane reveal. Cuts on matched motion; 180 degree shutter.')
    for obj in bpy.data.objects:
        for modifier in obj.modifiers:
            if modifier.type == 'MESH_CACHE':
                modifier.filepath = '//cache/' + Path(modifier.filepath).name
    sc.frame_set(1)
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'Golden_Hour_Forest_Retreat.blend'), compress=True,
                                relative_remap=False)
    report = dict(blender=bpy.app.version_string, polish=polish, objects=len(bpy.data.objects),
                  vertices=sum(len(x.vertices) for x in bpy.data.meshes),
                  polygons=sum(len(x.polygons) for x in bpy.data.meshes),
                  cameras=[m.camera.name for m in sc.timeline_markers], timeline=[1, sc.frame_end])
    (OUT / 'review' / 'scene_inventory.json').write_text(json.dumps(report, indent=2))
    print('V3_BUILD_COMPLETE', json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
