"""Reuse only proven-equivalent pilot frames while rerendering changed shots."""
import argparse
import csv
import hashlib
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent


def digest(path):
    with path.open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()


def read_csv(path):
    with path.open() as handle:return {int(row['frame']):row for row in csv.DictReader(handle)}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',required=True)
    p.add_argument('--destination',required=True)
    p.add_argument('--changed-shots',required=True)
    args=p.parse_args()
    assert args.source.isalnum() and args.destination.isalnum() and args.source!=args.destination
    old=OUT/'review'/('pilot_'+args.source)
    new=OUT/'review'/('pilot_'+args.destination)
    assert not new.exists(),'Use a fresh pilot destination.'
    destination_scene_sha256=digest(OUT/'Golden_Hour_Forest_Retreat.blend')
    changed=set(args.changed_shots.split(','))
    source_input=json.loads((OUT/'review'/('pilot_'+args.source+'_v7')/'input.json').read_text())
    old_plan={s['id']:s for s in json.loads((old/'shot_plan.json').read_text())}
    new_plan={s['id']:s for s in json.loads((OUT/'review/shot_plan.json').read_text())}
    assert set(old_plan)==set(new_plan) and changed<=set(new_plan)
    for key in old_plan:
        assert old_plan[key]['frames']==new_plan[key]['frames']
        if key not in changed:assert old_plan[key]==new_plan[key]
    for name,value in source_input['source_scripts_sha256'].items():
        if name!='story.py':assert digest(OUT/'scripts'/name)==value,name
    assert digest(OUT/'scripts/render_retreat.py')==source_input['render_script_sha256']
    assert digest(OUT/'cache/pool_gravity_capillary.mdd')==source_input['water_cache_sha256']
    old_model=json.loads((old/'scene_inventory.json').read_text())
    new_model=json.loads((OUT/'review/scene_inventory.json').read_text())
    assert old_model['source_scene_sha256']==new_model['source_scene_sha256']==digest(OUT/'source/v6_scene.blend')
    assert old_model['model_fingerprint_after']==new_model['model_fingerprint_after']
    old_motion=read_csv(old/'camera_path.csv');new_motion=read_csv(OUT/'review/camera_path.csv')
    frames=sorted(f for s in new_plan.values() if s['id'] not in changed for f in range(s['frames'][0],s['frames'][1]+1))
    assert all(old_motion[f]==new_motion[f] for f in frames)
    receipts={}
    for path in (old/'frames').glob('render_gpu_*.jsonl'):
        for line in path.read_text().splitlines():
            row=json.loads(line);receipts[row['frame']]=row
    hashes=json.loads((OUT/'review'/('pilot_'+args.source+'_frame_hashes.json')).read_text())
    (new/'frames').mkdir(parents=True)
    reused=[]
    def copy_frame(frame):
        name=f'frame_{frame:04d}.png';src=old/'frames'/name;dest=new/'frames'/name
        assert src.stat().st_size==receipts[frame]['bytes']
        shutil.copy2(src,dest)
        assert digest(dest)==hashes[name]
        row=dict(receipts[frame],file=str(dest),reused_from=str(src),reuse_source_scene_sha256=source_input['blend_sha256'])
        return frame,row,hashes[name]
    with ThreadPoolExecutor(max_workers=12) as executor,(new/'frames/render_gpu_reused.jsonl').open('x') as handle:
        for frame,row,value in executor.map(copy_frame,frames):
            handle.write(json.dumps(row)+'\n')
            reused.append(dict(frame=frame,sha256=value))
    for name in ('shot_plan.json','project_validation.json','scene_inventory.json','camera_path.csv'):
        shutil.copy2(OUT/'review'/name,new/name)
    assert digest(OUT/'Golden_Hour_Forest_Retreat.blend')==destination_scene_sha256
    report=dict(source_take=args.source,destination_take=args.destination,changed_shots=sorted(changed),
        source_scene_sha256=source_input['blend_sha256'],destination_scene_sha256=destination_scene_sha256,
        source_input_sha256=digest(OUT/'review'/('pilot_'+args.source+'_v7')/'input.json'),
        model_fingerprint=new_model['model_fingerprint_after'],water_cache_sha256=source_input['water_cache_sha256'],
        reused_frames=reused,rerendered_frames=len(new_motion)-len(frames),
        equivalence='Unchanged shot definitions, frame times, every camera-state CSV field, source scene, non-camera model fingerprint, renderer and supporting authoring code, water cache. Copied PNG hashes match the fully verified previous pilot.')
    (OUT/'review'/('pilot_'+args.destination+'_reuse.json')).write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(reused_frames=len(frames),frames_to_render=report['rerendered_frames']),indent=2),flush=True)


if __name__=='__main__':main()
