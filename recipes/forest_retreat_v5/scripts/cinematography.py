"""Camera choreography helpers: authored shots with arc-length splines and eased velocity.

Each move is a centripetal Catmull-Rom path through authored waypoints. The
path is re-parameterised by arc length, so speed follows an explicit velocity
profile instead of control-point spacing. Look targets use their own arc-length
curve, lens and focus are keyed along the move, and a very small low-frequency
float keeps locked-off moves from reading as mechanical. The horizon is always
level. Cuts land on motion with matching direction; only the film start and
end come to rest.
"""
import csv
import json
import math
from pathlib import Path

from common import *
from mathutils import Euler

OUT = Path(__file__).resolve().parent.parent
FPS = 24
FRAME_END = 1008


# ---------------------------------------------------------------- curves ---

def catmull_rom(points, u):
    """Centripetal Catmull-Rom through all points; u in [0, 1]."""
    pts = [Vector(p) for p in points]
    if len(pts) == 1:
        return pts[0].copy()
    pts = [2 * pts[0] - pts[1]] + pts + [2 * pts[-1] - pts[-2]]
    segments = len(pts) - 3
    x = min(max(u, 0), 1) * segments
    i = min(int(x), segments - 1)
    t = x - i
    p0, p1, p2, p3 = pts[i:i + 4]

    def knot(ti, a, b):
        return ti + max((b - a).length, 1e-6) ** .5
    t0 = 0
    t1 = knot(t0, p0, p1)
    t2 = knot(t1, p1, p2)
    t3 = knot(t2, p2, p3)
    tt = t1 + (t2 - t1) * t
    a1 = (t1 - tt) / (t1 - t0) * p0 + (tt - t0) / (t1 - t0) * p1
    a2 = (t2 - tt) / (t2 - t1) * p1 + (tt - t1) / (t2 - t1) * p2
    a3 = (t3 - tt) / (t3 - t2) * p2 + (tt - t2) / (t3 - t2) * p3
    b1 = (t2 - tt) / (t2 - t0) * a1 + (tt - t0) / (t2 - t0) * a2
    b2 = (t3 - tt) / (t3 - t1) * a2 + (tt - t1) / (t3 - t1) * a3
    return (t2 - tt) / (t2 - t1) * b1 + (tt - t1) / (t2 - t1) * b2


class ArcLengthCurve:
    def __init__(self, points, samples=4000):
        self.points = points
        self.u = [i / samples for i in range(samples + 1)]
        pos = [catmull_rom(points, u) for u in self.u]
        self.length = [0.0]
        for a, b in zip(pos, pos[1:]):
            self.length.append(self.length[-1] + (b - a).length)
        self.total = self.length[-1]

    def at(self, s):
        """Point at normalised arc length s in [0, 1]."""
        if self.total < 1e-9:
            return Vector(self.points[0])
        goal = min(max(s, 0), 1) * self.total
        lo, hi = 0, len(self.length) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.length[mid] < goal:
                lo = mid
            else:
                hi = mid
        span = self.length[hi] - self.length[lo]
        k = 0 if span < 1e-12 else (goal - self.length[lo]) / span
        return catmull_rom(self.points, self.u[lo] + (self.u[hi] - self.u[lo]) * k)


def ease5(x):
    x = min(max(x, 0), 1)
    return x * x * x * (x * (6 * x - 15) + 10)


def progress(n, v_in, v_out, ramp_in, ramp_out):
    """Normalised distance for n+1 samples from a velocity profile.

    Velocity rises from v_in to the cruise speed over ramp_in, holds, and
    falls to v_out over ramp_out (fractions of the move). Quintic ramps give
    continuous acceleration, so moves start and settle without a jolt.
    """
    def v(tau):
        value = 1.0
        if ramp_in > 0 and tau < ramp_in:
            value = v_in + (1 - v_in) * ease5(tau / ramp_in)
        if ramp_out > 0 and tau > 1 - ramp_out:
            value = min(value, v_out + (1 - v_out) * ease5((1 - tau) / ramp_out))
        return value
    steps = 40 * max(n, 1)
    acc, out = 0.0, [0.0]
    for k in range(1, steps + 1):
        acc += (v((k - .5) / steps)) / steps
        if k % 40 == 0:
            out.append(acc)
    return [x / acc for x in out]


def keyed(keys, s):
    """Quintic interpolation of (s, value) keys; values may be floats or vectors."""
    if s <= keys[0][0]:
        return keys[0][1]
    for (s0, a), (s1, b) in zip(keys, keys[1:]):
        if s <= s1:
            k = ease5((s - s0) / max(s1 - s0, 1e-9))
            if isinstance(a, (tuple, list, Vector)):
                return Vector(a).lerp(Vector(b), k)
            return a + (b - a) * k
    return keys[-1][1]


def float_offset(frame, seed, scale):
    """Low-frequency operator float: metres and radians, sum of incommensurate sines."""
    t = frame / FPS
    def wave(f1, f2, f3, p):
        return (.55 * sin(2 * pi * f1 * t + p) + .30 * sin(2 * pi * f2 * t + 1.7 * p)
                + .15 * sin(2 * pi * f3 * t + 2.3 * p))
    pos = Vector((wave(.13, .31, .57, seed), wave(.11, .27, .49, seed + 1.1), wave(.17, .37, .61, seed + 2.3))) * .004 * scale
    rot = Vector((wave(.12, .29, .53, seed + 3.7), wave(.09, .23, .47, seed + 4.1) * .5,
                  wave(.10, .26, .44, seed + 5.9))) * math.radians(.06) * scale
    return pos, rot


# ----------------------------------------------------------------- shots ---
# Frames are inclusive. v_in / v_out are start / end speeds relative to cruise.

SHOTS = []  # Authored in story.py; populated by story.build().


# ----------------------------------------------------------------- build ---

def sample(shot):
    """Per-frame camera state for one shot, independent of Blender objects."""
    start, end = shot['frames']
    hold, hold_out = shot.get('hold', 0), shot.get('hold_out', 0)
    moving = end - start - hold - hold_out
    s_table = progress(moving, shot['v_in'], shot['v_out'], shot['ramp_in'], shot['ramp_out'])
    pos_curve, tgt_curve = ArcLengthCurve(shot['position']), ArcLengthCurve(shot['target'])
    states = []
    for frame in range(start, end + 1):
        k = min(max(frame - start - hold, 0), moving)
        s = s_table[k]
        pos, tgt = pos_curve.at(s), tgt_curve.at(s)
        focus = keyed(shot['focus'], s) if 'focus' in shot else tgt
        forward = (tgt - pos).normalized()
        # Float fades in after the opening hold so frame 1 stays exactly on the reference.
        weight = ease5((frame - start - hold) / 36) if hold else 1.0
        dpos, drot = float_offset(frame, float(shot['id']) * 1.37, shot['float'] * weight)
        states.append(dict(frame=frame, s=s, position=pos + dpos, target=tgt, float_rotation=drot,
                           lens=keyed(shot['lens'], s), fstop=keyed(shot['fstop'], s),
                           focus_distance=max(.2, (Vector(focus) - pos).dot(forward))))
    return states


def orient(obj, state, previous=None):
    obj.location = state['position']
    base = (state['target'] - state['position']).to_track_quat('-Z', 'Y').to_matrix()
    d = state['float_rotation']
    local = Euler((d.x, d.z, d.y), 'XYZ').to_matrix()
    # Keep Euler angles continuous with the previous key. Without this a heading
    # through +-180 degrees wraps by 360 degrees between keys, and the linearly
    # interpolated camera spins inside the motion-blur shutter.
    obj.rotation_euler = (base @ local).to_euler('XYZ', previous) if previous else (base @ local).to_euler('XYZ')
    return obj.rotation_euler.copy()


def make_camera(name):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    link_object(obj)
    data.sensor_fit = 'HORIZONTAL'
    data.sensor_width = 36
    data.clip_start = .035
    data.clip_end = 300
    data.dof.use_dof = True
    data.dof.aperture_blades = 9
    data.dof.aperture_ratio = 1.0
    return obj


def build(m=None):
    sc = bpy.context.scene
    for obj in list(bpy.data.objects):
        if obj.type == 'CAMERA' and not obj.name.startswith('Still / '):
            bpy.data.objects.remove(obj, do_unlink=True)
    sc.timeline_markers.clear()
    collection('59 • Retreat / cinematic camera choreography')
    if sc.animation_data and sc.animation_data.action:
        for fc in list(sc.animation_data.action.fcurves):
            if fc.data_path == 'view_settings.exposure':
                sc.animation_data.action.fcurves.remove(fc)
    records = []
    for shot in SHOTS:
        cam = make_camera(shot['id'] + ' / ' + shot['name'])
        cam['intent'] = shot['intent']
        cam['path'] = ('centripetal Catmull-Rom waypoints, arc-length parameterised; quintic velocity '
                       'profile v_in=%.2f v_out=%.2f; level horizon; keyed lens and focus' % (shot['v_in'], shot['v_out']))
        previous = None
        for state in sample(shot):
            previous = orient(cam, state, previous)
            cam.data.lens = state['lens']
            cam.data.dof.aperture_fstop = state['fstop']
            cam.data.dof.focus_distance = state['focus_distance']
            f = state['frame']
            cam.keyframe_insert('location', frame=f)
            cam.keyframe_insert('rotation_euler', frame=f)
            cam.data.keyframe_insert('lens', frame=f)
            cam.data.dof.keyframe_insert('focus_distance', frame=f)
            cam.data.dof.keyframe_insert('aperture_fstop', frame=f)
            records.append(dict(shot=shot['id'], frame=f, x=state['position'].x, y=state['position'].y,
                                z=state['position'].z, tx=state['target'].x, ty=state['target'].y,
                                tz=state['target'].z, lens=state['lens'], fstop=state['fstop'],
                                focus=state['focus_distance']))
        for data in (cam, cam.data):
            for fc in data.animation_data.action.fcurves:
                for key in fc.keyframe_points:
                    key.interpolation = 'LINEAR'
        marker = sc.timeline_markers.new(shot['id'] + ' / ' + shot['name'], frame=shot['frames'][0])
        marker.camera = cam
        sc.view_settings.exposure = shot['exposure']
        sc.view_settings.keyframe_insert('exposure', frame=shot['frames'][0])
    for fc in sc.animation_data.action.fcurves:
        if fc.data_path == 'view_settings.exposure':
            for key in fc.keyframe_points:
                key.interpolation = 'CONSTANT'
    sc.camera = sc.timeline_markers[0].camera
    sc.frame_start, sc.frame_end = 1, FRAME_END
    sc.render.motion_blur_shutter = .5
    review = OUT / 'review'
    review.mkdir(exist_ok=True)
    with (review / 'camera_path.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    plan = [{k: (list(v) if isinstance(v, tuple) else v) for k, v in shot.items()} for shot in SHOTS]
    (review / 'shot_plan.json').write_text(json.dumps(plan, indent=2, default=list))
    sc.frame_set(1)
    return records
