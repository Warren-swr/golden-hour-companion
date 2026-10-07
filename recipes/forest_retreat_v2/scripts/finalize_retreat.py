"""Set the reviewed lighting balance and portable final opening state."""
import json
from pathlib import Path

import bpy

OUT = Path(__file__).resolve().parent.parent
scene = bpy.context.scene
bpy.data.objects['Warm reading lamp practical'].data.energy = 5
bpy.data.objects['Living / woven reading pendant practical'].data.energy = 72
scene.cycles.use_auto_tile = False
scene.cycles.samples = 192
scene.cycles.adaptive_threshold = .013
scene.render.resolution_x = scene.render.resolution_y = 2160
scene.render.use_motion_blur = True
scene.render.motion_blur_shutter = .28
scene['lighting_review'] = 'Selected 72 W woven living pendant and 5 W reading practical; sun, sky and exposure fixed across all eight shots.'
for data in bpy.data.meshes:
    if any(mat and 'bark' in mat.name.lower() for mat in data.materials):
        for polygon in data.polygons:
            if len(polygon.vertices) > 4:
                polygon.use_smooth = False
for obj in bpy.data.objects:
    for modifier in obj.modifiers:
        if modifier.type == 'MESH_CACHE':
            modifier.filepath = '//cache/' + Path(modifier.filepath).name
for img in bpy.data.images:
    if img.source == 'FILE' and img.packed_file:
        img.filepath = '//assets/textures/' + Path(img.filepath).name
scene.frame_set(1)
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces.active.shading.type = 'SOLID'
        area.spaces.active.region_3d.view_perspective = 'CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Golden_Hour_Forest_Retreat.blend'), compress=True,
                          relative_remap=False)
print('REVIEWED_SCENE_FROZEN', bpy.data.filepath, flush=True)
