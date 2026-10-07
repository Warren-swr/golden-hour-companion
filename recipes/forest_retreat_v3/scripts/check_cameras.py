"""Per-frame camera review: clearance to geometry, speed, acceleration and opening lock."""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parent.parent
V2_OPENING = dict(location=(0.26, -2.75, 1.41), rotation=(1.5490784645070566, 0.0, 0.09426525235176086),
                  lens=54.0, focus=2.7629151344299316)


def directions():
    dirs = []
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            for z in (-1, 0, 1):
                if x or y or z:
                    dirs.append(Vector((x, y, z)).normalized())
    return dirs


def main():
    sc = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    markers = sorted((m.frame, m.camera) for m in sc.timeline_markers)
    dirs = directions()
    per_shot, prev = {}, None
    history = []
    for frame in range(sc.frame_start, sc.frame_end + 1):
        cam = [c for f, c in markers if f <= frame][-1]
        sc.frame_set(frame)
        mw = cam.matrix_world.copy()
        origin = mw.translation.copy()
        forward = (mw.to_3x3() @ Vector((0, 0, -1))).normalized()
        clearance = 1.0
        for d in dirs:
            hit, loc, *_ = sc.ray_cast(depsgraph, origin, d, distance=1.0)
            if hit:
                clearance = min(clearance, (loc - origin).length)
        hit, loc, _, _, obj, _ = sc.ray_cast(depsgraph, origin, forward, distance=60)
        ahead = (loc - origin).length if hit else 60
        rec = per_shot.setdefault(cam.name, dict(frames=[frame, frame], min_clearance=1.0, min_clearance_frame=frame,
                                                  min_ahead=60, min_ahead_frame=frame, min_ahead_object='',
                                                  max_speed=0, max_angular_deg_s=0, max_accel=0, path_m=0))
        rec['frames'][1] = frame
        if clearance < rec['min_clearance']:
            rec['min_clearance'], rec['min_clearance_frame'] = clearance, frame
        if ahead < rec['min_ahead']:
            rec['min_ahead'], rec['min_ahead_frame'] = ahead, frame
            rec['min_ahead_object'] = obj.name if hit else ''
        if prev and prev[0] == cam.name:
            v = (origin - prev[1]) * 24
            ang = math.degrees(forward.angle(prev[2], 0)) * 24
            rec['max_speed'] = max(rec['max_speed'], v.length)
            rec['max_angular_deg_s'] = max(rec['max_angular_deg_s'], ang)
            rec['path_m'] += (origin - prev[1]).length
            if prev[3] is not None:
                rec['max_accel'] = max(rec['max_accel'], ((v - prev[3]) * 24).length)
            prev = (cam.name, origin, forward, v)
        else:
            prev = (cam.name, origin, forward, None)
        history.append(dict(frame=frame, camera=cam.name, clearance=round(clearance, 3), ahead=round(ahead, 3)))
    sc.frame_set(1)
    cam = markers[0][1]
    opening = dict(location=list(cam.matrix_world.translation), rotation=list(cam.rotation_euler),
                   lens=cam.data.lens, focus=cam.data.dof.focus_distance)
    delta = max(max(abs(a - b) for a, b in zip(opening['location'], V2_OPENING['location'])),
                max(abs(a - b) for a, b in zip(opening['rotation'], V2_OPENING['rotation'])),
                abs(opening['lens'] - V2_OPENING['lens']), abs(opening['focus'] - V2_OPENING['focus']))
    for f in (2, 48):
        sc.frame_set(f)
        delta = max(delta, (cam.matrix_world.translation - Vector(V2_OPENING['location'])).length)
    report = dict(opening_matches_v2=delta < 1e-5, opening_max_delta=delta, shots=per_shot)
    (OUT / 'review' / 'camera_motion_metrics.json').write_text(json.dumps(report, indent=2))
    (OUT / 'review' / 'camera_clearance_per_frame.json').write_text(json.dumps(history))
    print('CAMERA_CHECK', json.dumps(report, indent=1), flush=True)


if __name__ == '__main__':
    main()
