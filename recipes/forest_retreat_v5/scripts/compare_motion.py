"""Confirm that post-pilot static refinements preserve every camera animation curve."""
import hashlib
import json
from pathlib import Path

import bpy

OUT=Path(__file__).resolve().parent.parent


def camera_curves(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    sc=bpy.context.scene
    result=[]
    for marker in sorted(sc.timeline_markers,key=lambda m:m.frame):
        camera=marker.camera
        curves=[]
        for label,block in (('object',camera),('data',camera.data)):
            for fc in block.animation_data.action.fcurves:
                curves.append(dict(block=label,path=fc.data_path,index=fc.array_index,
                                   keys=[(tuple(p.co),p.interpolation) for p in fc.keyframe_points]))
        result.append(dict(frame=marker.frame,name=camera.name,curves=curves))
    return result


def main():
    pilot=camera_curves(OUT/'source/v4_scene.blend')
    final=camera_curves(OUT/'Golden_Hour_Forest_Retreat.blend')
    equal=pilot==final
    result=dict(all_camera_curves_identical=equal,shots=len(final),
                pilot_camera_sha256=hashlib.sha256(json.dumps(pilot,sort_keys=True).encode()).hexdigest(),
                final_camera_sha256=hashlib.sha256(json.dumps(final,sort_keys=True).encode()).hexdigest(),
                changes_since_pilot='Window leaf material assignment, anatomical surface, veins and petioles only; no camera or edit changes.')
    (OUT/'review/pilot_to_final_motion.json').write_text(json.dumps(result,indent=2))
    assert equal
    print('CAMERA_CURVES_IDENTICAL',flush=True)


if __name__=='__main__':
    main()
