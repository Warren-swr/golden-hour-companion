"""Verify a relocated model using only the blend and its water cache."""
import hashlib
import json
from pathlib import Path

import bpy

OUT = Path(__file__).resolve().parent.parent
scene = bpy.context.scene
water = bpy.data.objects['Pool / baked gravity-capillary water volume']
cache = Path(bpy.path.abspath(water.modifiers[0].filepath))
missing = [img.filepath for img in bpy.data.images if img.source == 'FILE' and not img.packed_file
           and not Path(bpy.path.abspath(img.filepath)).exists()]
scene.frame_set(684)
mesh = water.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
samples = [mesh.vertices[i].co.z for i in range(0, 37837, 173)]
invalid_drivers = []
for datablocks in (bpy.data.objects, bpy.data.shape_keys):
    for data in datablocks:
        if data.animation_data:
            for curve in data.animation_data.drivers:
                if not curve.driver.is_valid:
                    invalid_drivers.append((data.name, curve.data_path))
report = dict(opened=bpy.data.filepath, relocated=True, cache=str(cache),
              cache_exists=cache.exists(), missing_images=missing, invalid_drivers=invalid_drivers,
              packed_texture_count=sum(bool(i.packed_file) for i in bpy.data.images),
              water_height_range=[min(samples),max(samples)],
              blend_sha256=hashlib.file_digest(open(bpy.data.filepath, 'rb'),'sha256').hexdigest())
if missing or invalid_drivers or not cache.exists() or max(samples)-min(samples)<.004:
    raise RuntimeError(json.dumps(report))
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 4
scene.cycles.use_denoising = False
scene.render.use_motion_blur = False
scene.render.resolution_x = scene.render.resolution_y = 256
scene.render.filepath = str(OUT/'review/portable_reopen_render.png')
bpy.ops.render.render(write_still=True)
report['cpu_render_completed'] = True
(OUT/'review/portable_validation.json').write_text(json.dumps(report, indent=2))
print('PORTABLE_PROJECT_PASS', json.dumps(report), flush=True)
