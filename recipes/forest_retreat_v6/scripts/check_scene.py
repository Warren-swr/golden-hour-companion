"""Reopen validation and geometric camera checks; does not change saved scene."""
import json
import hashlib
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

OUT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(OUT/'scripts'))
from story import SHOTS
from film import FRAMES,SHOT_COUNT
from cinematography import sample, orient


def main():
    sc=bpy.context.scene
    scene_path=Path(bpy.data.filepath)
    scene_hash=hashlib.file_digest(scene_path.open('rb'),'sha256').hexdigest()
    missing=[]
    for im in bpy.data.images:
        if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists():
            missing.append(im.filepath)
    caches=[]
    # Geometric camera clearance is against solid architecture/furniture and static flora.
    # Temporarily freeze the 1–2 cm breeze and water to avoid rebuilding their BVH 1008 times.
    for key in bpy.data.shape_keys:
        if key.animation_data:
            for driver in key.animation_data.drivers:
                driver.mute=True
    for ob in bpy.data.objects:
        for mod in ob.modifiers:
            if mod.type=='MESH_CACHE':
                path=Path(bpy.path.abspath(mod.filepath))
                caches.append(dict(object=ob.name,path=str(path),exists=path.exists()))
                mod.show_viewport=False
        if ob.name.startswith('Pool / falling spray bead') and ob.animation_data:
            for driver in ob.animation_data.drivers:
                driver.mute=True
    sc.frame_set(1)
    opening=sc.camera
    expected=dict(location=(.26,-2.75,1.41),rotation=(1.5490784645070566,0,.09426525235176086),
                  lens=54.0,focus=2.7629151344299316)
    opening_delta=max(max(abs(a-b) for a,b in zip(opening.location,expected['location'])),
                      max(abs(a-b) for a,b in zip(opening.rotation_euler,expected['rotation'])),
                      abs(opening.data.lens-expected['lens']),abs(opening.data.dof.focus_distance-expected['focus']))
    deps=bpy.context.evaluated_depsgraph_get()
    dirs=[Vector((x,y,z)).normalized() for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1) if x or y or z]
    records=[]
    per_shot=[]
    for shot in SHOTS:
        states=sample(shot)
        previous=None
        stat=dict(id=shot['id'],name=shot['name'],frames=shot['frames'],min_clearance=2,
                  max_speed=0,max_angular_deg_s=0,min_ahead=60,nearby_object='',max_subframe_rotation_deg=0)
        cam=bpy.data.objects[shot['id']+' / '+shot['name']]
        for state in states:
            pos=state['position']; forward=(state['target']-pos).normalized()
            clearance=2; nearest=''
            for d in dirs:
                hit,location,normal,index,ob,matrix=sc.ray_cast(deps,pos,d,distance=2)
                if hit and (location-pos).length<clearance:
                    clearance=(location-pos).length; nearest=ob.name
            hit,location,normal,index,ob,matrix=sc.ray_cast(deps,pos,forward,distance=60)
            ahead=(location-pos).length if hit else 60
            if clearance<stat['min_clearance']:
                stat.update(min_clearance=clearance,nearest_frame=state['frame'],nearby_object=nearest)
            stat['min_ahead']=min(stat['min_ahead'],ahead)
            if previous:
                stat['max_speed']=max(stat['max_speed'],(pos-previous['position']).length*24)
                stat['max_angular_deg_s']=max(stat['max_angular_deg_s'],math.degrees(forward.angle(previous['forward'],0))*24)
            previous=dict(position=pos.copy(),forward=forward)
            records.append(dict(frame=state['frame'],shot=shot['id'],clearance=round(clearance,4),ahead=round(ahead,4)))
        # Validate the actual saved camera curves for Euler wraps inside the shutter.
        curves={fc.array_index:fc for fc in cam.animation_data.action.fcurves if fc.data_path=='rotation_euler'}
        for frame in range(shot['frames'][0],shot['frames'][1]):
            delta=max(abs(fc.evaluate(frame+.25)-fc.evaluate(frame-.25)) for fc in curves.values())
            stat['max_subframe_rotation_deg']=max(stat['max_subframe_rotation_deg'],math.degrees(delta))
        per_shot.append(stat)
        print('CAMERA_REVIEW',json.dumps(stat),flush=True)
    report=dict(scene_sha256=scene_hash,missing_images=missing,caches=caches,shots=per_shot,
                opening_camera_matches_reference=opening_delta<1e-5,opening_camera_max_delta=opening_delta,
                initial_hold_frames=0,frames=sc.frame_end,fps=sc.render.fps,
                packed_images=sum(bool(i.packed_file) for i in bpy.data.images),
                review_scope='26-ray clearance for every authored camera frame; 2cm breeze frozen; saved Euler subframes checked')
    (OUT/'review/project_validation.json').write_text(json.dumps(report,indent=2))
    (OUT/'review/camera_clearance_per_frame.json').write_text(json.dumps(records))
    assert not missing and all(c['exists'] for c in caches)
    assert opening_delta<1e-5
    assert len(sc.timeline_markers)==SHOT_COUNT and sc.frame_end==FRAMES
    assert min(x['min_clearance'] for x in per_shot)>.12
    assert max(x['max_subframe_rotation_deg'] for x in per_shot)<3
    print('SCENE_CHECK_COMPLETE',flush=True)


if __name__=='__main__':
    main()
