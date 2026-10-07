"""Build v4 from an untouched, hashed v3 scene snapshot."""
import json
import argparse
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
sys.path.insert(0, str(HERE))
import refine_scene
import story


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='Golden_Hour_Forest_Retreat.blend')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    bpy.ops.wm.open_mainfile(filepath=str(OUT / 'source/v3_scene.blend'))
    sc = bpy.context.scene
    sc.frame_set(1)
    for ob in bpy.data.objects:
        for mod in ob.modifiers:
            if mod.type == 'MESH_CACHE':
                mod.filepath = str(OUT / 'cache' / Path(mod.filepath).name)
    polish = refine_scene.build()
    print('REFINEMENT_COMPLETE',flush=True)
    story.build()
    print('STORY_COMPLETE',flush=True)
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 256
    sc.cycles.adaptive_threshold = .010
    sc.cycles.denoising_quality = 'HIGH'
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = .5
    sc.render.resolution_x = sc.render.resolution_y = 2160
    sc.render.fps = 24
    sc['production_revision'] = 'forest_retreat_v4 / architectural narrative and material refinement'
    sc['render_contract'] = '1008 distinct native Cycles frames, 2160 square, 24 fps, 42 seconds, 9 shots'
    sc['animation'] = 'Immediate opening move; varied medium/wide spatial narrative; fixed afternoon sun; no detail inserts.'
    for ob in bpy.data.objects:
        for mod in ob.modifiers:
            if mod.type == 'MESH_CACHE':
                mod.filepath = '//cache/' + Path(mod.filepath).name
    for img in bpy.data.images:
        if img.source == 'FILE' and img.packed_file:
            img.filepath = '//assets/textures/' + Path(img.filepath).name
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / args.out), compress=True,
                              relative_remap=False)
    result = dict(blender=bpy.app.version_string,polish=polish,
                  objects=len(bpy.data.objects),vertices=sum(len(m.vertices) for m in bpy.data.meshes),
                  polygons=sum(len(m.polygons) for m in bpy.data.meshes),
                  cameras=[m.camera.name for m in sc.timeline_markers],frames=1008,fps=24)
    (OUT / 'review/scene_inventory.json').write_text(json.dumps(result,indent=2))
    print('V4_BUILD_COMPLETE',json.dumps(result),flush=True)


if __name__ == '__main__':
    main()
