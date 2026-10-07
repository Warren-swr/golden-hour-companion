"""Rebuild the self-contained retreat revision from the preserved source scene."""
import json
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
sys.path.insert(0, str(HERE))
import retreat_materials
import retreat_architecture
import retreat_interior
import retreat_landscape
import retreat_pool
import retreat_cameras


def main():
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'source'/'base_scene.blend'))
    m = retreat_materials.build()
    for module in (retreat_architecture, retreat_interior, retreat_landscape, retreat_pool, retreat_cameras):
        print('RETREAT_STAGE', module.__name__, flush=True)
        module.build(m)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'GPU'
    sc.cycles.samples = 192
    sc.cycles.adaptive_threshold = .013
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.denoising_quality = 'HIGH'
    sc.cycles.max_bounces = 12
    sc.cycles.diffuse_bounces = 5
    sc.cycles.glossy_bounces = 6
    sc.cycles.transmission_bounces = 10
    sc.cycles.transparent_max_bounces = 16
    sc.cycles.caustics_refractive = True
    sc.cycles.caustics_reflective = True
    sc.cycles.sample_clamp_indirect = 5
    sc.cycles.seed = 260926
    sc.cycles.use_auto_tile = False
    sc.cycles.use_animated_seed = False
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.data.type == 'SUN':
            obj.data.cycles.is_caustics_light = True
    sc.render.resolution_x = 2160
    sc.render.resolution_y = 2160
    sc.render.resolution_percentage = 100
    sc.render.fps = 24
    sc.render.fps_base = 1
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = .28
    sc.render.use_persistent_data = True
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.image_settings.color_depth = '8'
    sc.render.image_settings.compression = 25
    sc.render.filepath = '//frames/frame_'
    sc.frame_start, sc.frame_end = 1, 1056
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.view_settings.exposure = 0
    sc['production_revision'] = 'forest_retreat_v2 / cedar cabin, inhabited interiors, garden and simulated pool'
    sc['render_contract'] = 'Native 2160 square, 24 fps, 1056 source frames, 44 seconds, 8 spatially curved camera moves'
    sc['water_simulation'] = 'Portable MDD cache: finite-depth gravity-capillary basin modes. See review/water_simulation.json.'
    sc['assets'] = 'Original geometry and packed CC0 Poly Haven material maps, with exact provenance in assets/sources.json'
    sc['reference_usage'] = 'Original cushion corner retained as real 3D; the reference JPEG is external comparison only.'
    sc['animation'] = 'Eight independent editorial shots, fixed golden-hour sun and exposure; no image warping or generated video.'
    sc.frame_set(1)
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
    # Make every texture path relative even though all image data are packed.
    for img in bpy.data.images:
        if img.source == 'FILE' and img.packed_file:
            img.filepath = '//assets/textures/' + Path(img.filepath).name
    for obj in bpy.data.objects:
        for modifier in obj.modifiers:
            if modifier.type == 'MESH_CACHE':
                modifier.filepath = '//cache/' + Path(modifier.filepath).name
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Golden_Hour_Forest_Retreat.blend'), compress=True,
                              relative_remap=False)
    report = dict(blender=bpy.app.version_string, objects=len(bpy.data.objects),
                  meshes=len(bpy.data.meshes), materials=len(bpy.data.materials),
                  vertices=sum(len(x.vertices) for x in bpy.data.meshes),
                  polygons=sum(len(x.polygons) for x in bpy.data.meshes),
                  packed_images=len([i for i in bpy.data.images if i.packed_file]),
                  timeline=[1,1056], resolution=[2160,2160], fps=24)
    (OUT/'review'/'scene_inventory.json').write_text(json.dumps(report, indent=2))
    print('RETREAT_BUILD_COMPLETE', json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
