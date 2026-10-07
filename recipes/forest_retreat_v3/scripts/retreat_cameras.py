"""Eight authored 3D camera moves with cubic spatial arcs and fixed lighting."""
import json
from pathlib import Path

from common import *

OUT = Path(__file__).resolve().parent.parent


def cubic(points, t):
    a, b, c, d = [Vector(p) for p in points]
    return (1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t*t*c + t**3*d


def camera(name, position, target, lens, fstop):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    link_object(obj)
    obj.location = position
    aim(obj, target)
    data.lens = lens
    data.sensor_width = 36
    data.clip_start = .035
    data.clip_end = 300
    data.dof.use_dof = True
    data.dof.aperture_blades = 9
    data.dof.aperture_fstop = fstop
    data.dof.focus_distance = (Vector(target)-obj.location).length
    return obj


SHOTS = [
    dict(id='01', name='The familiar afternoon', frames=[1,192], hold=48, lens=[54,31], fstop=[8,6.3],
         position=[(.26,-2.75,1.41),(.40,-3.38,1.43),(.74,-4.22,1.79),(1.26,-4.53,1.81)],
         target=[(0,0,1.35),(-.04,-.02,1.30),(-.29,-.60,1.19),(-.35,-.89,1.16)],
         intent='Two-second reference hold, then a gentle curved retreat into the inhabited room.'),
    dict(id='02', name='A room for slow living', frames=[193,312], lens=[35,39], fstop=[4.5,5.0],
         position=[(1.31,-1.44,1.65),(1.31,-1.64,1.57),(1.18,-1.82,1.58),(.99,-1.83,1.65)],
         target=[(-2.43,-3.32,1.03),(-2.49,-3.39,1.01),(-2.59,-3.40,1.07),(-2.66,-3.26,1.12)],
         intent='A cross-room arc: foreground table and linen sofa lead toward the stove and forest window.'),
    dict(id='03', name='The texture of breakfast', frames=[313,408], lens=[51,55], fstop=[3.5,4.0],
         position=[(.72,-1.83,1.48),(.76,-2.02,1.56),(1.03,-2.15,1.66),(1.19,-2.09,1.67)],
         target=[(2.30,-.43,1.18),(2.37,-.42,1.17),(2.48,-.34,1.17),(2.57,-.31,1.20)],
         intent='An oblique still-life move across hand-laid tiles, cut lemon, bottles and the sink.'),
    dict(id='04', name='Linen and leaves', frames=[409,528], lens=[28,31], fstop=[5,5.6],
         position=[(3.65,-2.97,1.63),(3.77,-3.07,1.60),(4.11,-3.08,1.72),(4.38,-2.99,1.77)],
         target=[(5.12,-1.11,1.18),(5.26,-1.06,1.11),(5.47,-1.10,1.10),(5.65,-1.18,1.12)],
         intent='Curved bedside reveal: raked cloth, pleated curtains and the forest beyond the window.'),
    dict(id='05', name='Across the threshold', frames=[529,624], lens=[32,35], fstop=[5.6,6.3],
         position=[(1.91,-4.77,1.64),(1.81,-5.62,1.56),(2.39,-6.26,1.49),(2.85,-6.67,1.58)],
         target=[(1.63,-11.37,.04),(1.73,-12.01,-.04),(1.91,-12.32,-.02),(2.13,-12.69,.03)],
         intent='A real doorway crossing on a curved dolly, revealing the garden and water in one space.'),
    dict(id='06', name='Light on moving water', frames=[625,744], lens=[60,65], fstop=[4.5,5.0],
         position=[(3.05,-14.70,.40),(3.16,-14.38,.31),(3.55,-14.01,.37),(3.83,-13.91,.46)],
         target=[(4.72,-12.93,-.21),(4.90,-12.81,-.18),(5.04,-12.76,-.08),(5.10,-12.78,-.03)],
         intent='Low waterline arc toward the falling sheet, with reflections, ripples and refracted mosaic.'),
    dict(id='07', name='The pool garden', frames=[745,888], lens=[32,34], fstop=[8,8],
         position=[(7.66,-17.66,1.92),(8.80,-17.48,2.12),(9.65,-16.36,2.71),(9.53,-15.11,3.10)],
         target=[(.92,-8.80,1.08),(1.12,-8.23,1.16),(1.30,-7.76,1.26),(1.59,-7.29,1.40)],
         intent='A rising poolside orbit; furniture, water, porch and gable reveal in successive layers.'),
    dict(id='08', name='Home among the trees', frames=[889,1056], hold_out=24, lens=[35,39], fstop=[9,11],
         position=[(-7.65,-18.61,3.76),(-9.91,-18.25,4.49),(-10.75,-20.04,6.42),(-9.88,-22.09,7.86)],
         target=[(.76,-7.09,1.48),(.96,-6.71,1.63),(1.20,-6.02,1.88),(1.42,-5.91,2.00)],
         intent='Broad crane arc past the fire garden to a complete woodland cabin and pool portrait.'),
]


def build(m):
    for obj in list(bpy.data.objects):
        if obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)
    sc = bpy.context.scene
    sc.timeline_markers.clear()
    collection('59 • Retreat / cinematic camera choreography')
    for shot in SHOTS:
        start, end = shot['frames']
        cam = camera(shot['id']+' / '+shot['name'], shot['position'][0], shot['target'][0], shot['lens'][0], shot['fstop'][0])
        cam['intent'] = shot['intent']
        cam['path'] = 'cubic Bezier spatial path; independently curved look target; eased distance; sampled at every source frame'
        hold = shot.get('hold', 0)
        for frame in range(start, end+1):
            u = min(1, max(0, (frame-start-hold) / max(1, end-start-hold-shot.get('hold_out',0))))
            t = u*u*(3-2*u) if hold or shot.get('hold_out') else .65*u + .35*u*u*(3-2*u)
            cam.location = cubic(shot['position'], t)
            target = cubic(shot['target'], t)
            aim(cam, target)
            cam.data.lens = shot['lens'][0]*(1-t)+shot['lens'][1]*t
            cam.data.dof.aperture_fstop = shot['fstop'][0]*(1-t)+shot['fstop'][1]*t
            cam.data.dof.focus_distance = (target-cam.location).length
            cam.keyframe_insert(data_path='location', frame=frame)
            cam.keyframe_insert(data_path='rotation_euler', frame=frame)
            cam.data.keyframe_insert(data_path='lens', frame=frame)
            cam.data.dof.keyframe_insert(data_path='focus_distance', frame=frame)
            cam.data.dof.keyframe_insert(data_path='aperture_fstop', frame=frame)
        for data in (cam, cam.data):
            if data.animation_data and data.animation_data.action:
                for fc in data.animation_data.action.fcurves:
                    for key in fc.keyframe_points:
                        key.interpolation = 'LINEAR'
        marker = sc.timeline_markers.new(shot['id']+' / '+shot['name'], frame=start)
        marker.camera = cam
    sc.camera = sc.timeline_markers[0].camera
    camera('Still / exterior hero', (11.0,-19.7,6.0), (1.37,-7.02,1.90), 38, 11)
    camera('Still / pool at sunset', (6.92,-16.63,1.43), (1.24,-7.50,1.34), 32, 9)
    camera('Still / bedroom', (3.64,-3.05,1.79), (5.27,-1.29,1.12), 25, 8)
    camera('Still / living room', (1.12,-4.52,1.76), (-.77,-1.72,1.25), 28, 8)
    camera('Still / breakfast detail', (1.02,-1.94,1.67), (2.34,-.40,1.15), 48, 7)
    camera('Still / water optics', (3.49,-14.55,.43), (4.97,-12.80,-.11), 62, 7)
    camera('Still / fire garden', (-9.05,-14.63,1.62), (-2.72,-7.08,1.62), 29, 8)
    (OUT/'review'/'shot_plan.json').write_text(json.dumps(SHOTS, indent=2))
    sc.frame_set(1)
