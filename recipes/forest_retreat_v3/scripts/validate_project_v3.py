"""Reopen the saved v3 scene and check portability: images, cache, cameras, polish."""
import json
from pathlib import Path

import bpy

OUT = Path(__file__).resolve().parent.parent
sc = bpy.context.scene
missing_images = [i.name for i in bpy.data.images if i.source == 'FILE' and not i.packed_file
                  and not Path(bpy.path.abspath(i.filepath)).exists()]
caches = [(o.name, bpy.path.abspath(m.filepath)) for o in bpy.data.objects for m in o.modifiers if m.type == 'MESH_CACHE']
sheet = bpy.data.objects['Pool / gravity accelerated spillway water sheet']
report = dict(blend=bpy.data.filepath, blender=bpy.app.version_string, objects=len(bpy.data.objects),
              missing_images=missing_images, mesh_caches=[dict(object=n, path=p, exists=Path(p).exists()) for n, p in caches],
              shots=[dict(frame=m.frame, camera=m.camera.name) for m in sorted(sc.timeline_markers, key=lambda m: m.frame)],
              frame_range=[sc.frame_start, sc.frame_end], resolution=[sc.render.resolution_x, sc.render.resolution_y],
              fps=sc.render.fps, motion_blur_shutter=sc.render.motion_blur_shutter,
              firs=len([o for o in bpy.data.objects if o.name.startswith('Retreat silver fir ') and o.name.endswith('dense needle sprays')]),
              spillway_material=sheet.data.materials[0].name,
              spillway_solidify=any(m.type == 'SOLIDIFY' for m in sheet.modifiers),
              sewn_pillows=len([o for o in bpy.data.objects if o.name.startswith('Bedroom / sewn linen pillow') and o.type == 'MESH']))
report['passed'] = (not missing_images and all(c['exists'] for c in report['mesh_caches']) and len(report['shots']) == 6
                    and report['firs'] == 10 and not report['spillway_solidify'] and report['sewn_pillows'] == 2)
(OUT / 'review' / 'project_validation.json').write_text(json.dumps(report, indent=2))
print('PROJECT_VALIDATION', json.dumps(report), flush=True)
