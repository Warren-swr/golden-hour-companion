"""Verify each long take uses one continuous rendered camera path."""
import csv
import json
import math
from pathlib import Path

from film import LONG_TAKES,FPS,CUTS

OUT=Path(__file__).resolve().parent.parent


def main():
    plan=json.loads((OUT/'review/shot_plan.json').read_text())
    video=json.loads((OUT/'review/final_video_validation.json').read_text())
    project=json.loads((OUT/'review/project_validation.json').read_text())
    inputs=json.loads((OUT/'review/production_v7/input.json').read_text())
    assert project['scene_sha256']==inputs['blend_sha256']
    receipts={}
    for path in (OUT/'frames').glob('render_gpu_*.jsonl'):
        for line in path.read_text().splitlines():
            row=json.loads(line);receipts[row['frame']]=row
    with (OUT/'review/camera_path.csv').open() as handle:
        motion={int(row['frame']):row for row in csv.DictReader(handle)}
    result=[]
    for shot in plan:
        if shot['id'] not in LONG_TAKES:continue
        first,last=shot['frames'];frames=list(range(first,last+1))
        cameras={receipts[frame]['camera'] for frame in frames}
        assert cameras=={shot['id']+' / '+shot['name']}
        assert not (CUTS & set(frames[1:]))
        positions=[tuple(float(motion[frame][key]) for key in ('x','y','z')) for frame in frames]
        distance=sum(math.dist(a,b) for a,b in zip(positions,positions[1:]))
        lenses={float(motion[frame]['lens']) for frame in frames}
        assert distance>.6 and len(lenses)==1
        assert len(set(positions))>=len(frames)-4
        result.append(dict(id=shot['id'],name=shot['name'],frames=[first,last],seconds=len(frames)/FPS,
            rendered_frames=len(frames),camera=next(iter(cameras)),lens_mm=next(iter(lenses)),
            physical_camera_travel_metres=distance,average_travel_metres_per_second=distance/((len(frames)-1)/FPS),
            interior_cuts=[],distinct_camera_positions=len(set(positions))))
    assert len(result)==3
    report=dict(scene_sha256=inputs['blend_sha256'],movie_sha256=video['movie_sha256'],long_takes=result,
        method='Per-frame native render receipts and authored camera coordinates; no cuts inside each take; fixed lenses. Complete decode is recorded separately.')
    (OUT/'review/long_take_review.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
