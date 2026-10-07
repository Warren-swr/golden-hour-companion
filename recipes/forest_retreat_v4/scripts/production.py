"""A single resumable production process with a lock and bounded stages."""
import fcntl
import json
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent


def main():
    lock=(OUT/'review/production.lock').open('w')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    stages=[
        ('prepare',[sys.executable,str(OUT/'scripts/prepare_production.py')],120),
        ('render',[sys.executable,str(OUT/'scripts/render_jobs.py'),'--jobs',str(OUT/'review/production_jobs.json'),
                   '--gpus','0,1,2,3,4,5,6,7','--samples','256','--resolution','2160',
                   '--threshold','.010','--dynamic','--tag','production_v4'],21600),
        ('encode',[sys.executable,str(OUT/'scripts/assemble_v4.py'),
                   '--preview','Golden_Hour_Forest_Retreat_v4_1080_preview.mp4',
                   '--master','Golden_Hour_Forest_Retreat_v4_ProRes_HQ.mov'],3600),
        ('verify',['uv','run','--with','numpy','--with','pillow','python',str(OUT/'scripts/validate_video.py')],1800),
    ]
    def status(stage,value):
        result=dict(stage=stage,status=value,time_utc=datetime.now(timezone.utc).isoformat())
        tmp=OUT/'review/production_status.tmp';tmp.write_text(json.dumps(result,indent=2))
        tmp.replace(OUT/'review/production_status.json')
        print(json.dumps(result),flush=True)
    for stage,command,timeout in stages:
        status(stage,'running')
        try:
            with (OUT/'logs'/('production_'+stage+'.log')).open('w') as handle:
                subprocess.run(command,cwd=OUT,stdout=handle,stderr=subprocess.STDOUT,check=True,timeout=timeout)
        except BaseException:
            status(stage,'failed_preserved_for_review')
            raise
        status(stage,'complete')
    status('delivery','rendered_encoded_verified_pending_visual_review')


if __name__=='__main__':
    main()
