"""A single resumable production process with a lock and bounded stages."""
import argparse
import fcntl
import hashlib
import json
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    mode='pilot' if args.pilot else 'production'
    lock=(OUT/'review/production.lock').open('w')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if args.pilot:
        folder=OUT/'review/pilot_frames'
        folder.mkdir(exist_ok=True)
        jobs=[dict(frame=f,file=str(folder/('frame_%04d.png'%f)),color_depth='8') for f in range(1,1009)]
        (OUT/'review/pilot_jobs.json').write_text(json.dumps(jobs,indent=2))
        stages=[
            ('render',[sys.executable,str(OUT/'scripts/render_jobs.py'),'--jobs',str(OUT/'review/pilot_jobs.json'),
                       '--gpus','0,1,2,3,4,5,6,7','--samples','24','--resolution','576',
                       '--threshold','.045','--dynamic','--tag','pilot_v5'],1800),
            ('encode',[sys.executable,str(OUT/'scripts/assemble_v5.py'),'--frames','review/pilot_frames',
                       '--movie','Golden_Hour_Forest_Retreat_v5_pilot.mp4','--crf','19'],300),
            ('verify',['uv','run','--with','numpy','--with','pillow','python',str(OUT/'scripts/validate_video.py'),
                       '--movie','Golden_Hour_Forest_Retreat_v5_pilot.mp4','--frames','review/pilot_frames',
                       '--resolution','576','--tag','pilot'],300),
        ]
    else:
        gate=json.loads((OUT/'review/production_gate.json').read_text())
        with (OUT/'Golden_Hour_Forest_Retreat.blend').open('rb') as handle:
            scene_hash=hashlib.file_digest(handle,'sha256').hexdigest()
        assert gate['decision']=='ready_for_full_render' and gate['scene_sha256']==scene_hash
        stages=[
        ('prepare',[sys.executable,str(OUT/'scripts/prepare_production.py')],120),
        ('render',[sys.executable,str(OUT/'scripts/render_jobs.py'),'--jobs',str(OUT/'review/production_jobs.json'),
                   '--gpus','0,1,2,3,4,5,6,7','--samples','256','--resolution','2160',
                   '--threshold','.010','--dynamic','--tag','production_v5'],21600),
        ('encode',[sys.executable,str(OUT/'scripts/assemble_v5.py'),
                   '--preview','Golden_Hour_Forest_Retreat_v5_1080_preview.mp4',
                   '--master','Golden_Hour_Forest_Retreat_v5_ProRes_HQ.mov'],3600),
        ('verify',['uv','run','--with','numpy','--with','pillow','python',str(OUT/'scripts/validate_video.py')],1800),
        ]
    def status(stage,value):
        result=dict(mode=mode,stage=stage,status=value,time_utc=datetime.now(timezone.utc).isoformat())
        tmp=OUT/'review/production_status.tmp';tmp.write_text(json.dumps(result,indent=2))
        tmp.replace(OUT/'review/production_status.json')
        print(json.dumps(result),flush=True)
    for stage,command,timeout in stages:
        status(stage,'running')
        try:
            with (OUT/'logs'/(mode+'_'+stage+'.log')).open('w') as handle:
                subprocess.run(command,cwd=OUT,stdout=handle,stderr=subprocess.STDOUT,check=True,timeout=timeout)
        except BaseException:
            status(stage,'failed_preserved_for_review')
            raise
        status(stage,'complete')
    status('delivery','pilot_validated_pending_visual_review' if args.pilot else 'rendered_encoded_verified_pending_visual_review')


if __name__=='__main__':
    main()
