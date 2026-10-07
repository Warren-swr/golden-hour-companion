"""Compare shutter-interval camera matrices of two scene revisions.

Run inside Blender with: -- OLD.blend NEW.blend REPORT.json. Frames whose
shutter-open / centre / shutter-close matrices differ must be re-rendered.
"""
import json
import sys

import bpy

args = sys.argv[sys.argv.index('--') + 1:]
old, new, report_path = args


def sample(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    sc = bpy.context.scene
    half = sc.render.motion_blur_shutter / 2
    markers = sorted((m.frame, m.camera.name) for m in sc.timeline_markers)
    out, eulers = {}, {}
    for frame in range(1, sc.frame_end + 1):
        name = [n for f, n in markers if f <= frame][-1]
        cam = bpy.data.objects[name]
        mats = []
        for offset in (-half, 0, half):
            sc.frame_set(frame, subframe=0) if offset >= 0 else sc.frame_set(frame - 1, subframe=1 + offset)
            if offset > 0:
                sc.frame_set(frame, subframe=offset)
            mats.append([v for row in cam.matrix_world for v in row])
        out[frame] = mats
        eulers[frame] = (name, list(cam.rotation_euler))
    return out, eulers, half


a, ea, half = sample(old)
b, eb, _ = sample(new)
centre = max(max(abs(x - y) for x, y in zip(a[f][1], b[f][1])) for f in a)
affected = [f for f in a if max(max(abs(x - y) for x, y in zip(ma, mb)) for ma, mb in zip(a[f], b[f])) > 1e-4]
jumps = [f for f in range(2, len(eb) + 1) if eb[f][0] == eb[f - 1][0]
         and max(abs(x - y) for x, y in zip(eb[f][1], eb[f - 1][1])) > 1.0]
report = dict(old=old, new=new, shutter_half_frames=half, max_centre_matrix_difference=centre,
              frames_with_different_shutter_motion=affected, new_scene_euler_jumps_over_1_rad=jumps)
open(report_path, 'w').write(json.dumps(report, indent=2))
print('CAMERA_COMPARE', json.dumps(report), flush=True)
