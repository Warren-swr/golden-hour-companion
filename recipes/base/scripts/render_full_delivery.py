"""Reproducible final render, editorial assembly, and complete file verification."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser()
parser.add_argument('--gpus',default='1,2,3,4,5,6,7')
parser.add_argument('--skip-stills',action='store_true')
args=parser.parse_args()
stages=[('stills','render_stills.py',['--gpus',args.gpus]),
        ('animation','render_batch.py',['--gpus',args.gpus,'--samples','192']),
        ('assembly','assemble.py',[]),('video_verification','verify_video.py',[]),
        ('manifest','final_manifest.py',[])]
status={'started_utc':datetime.now(timezone.utc).isoformat(),'completed':[]}
if args.skip_stills:
    if len(list((OUT/'renders').glob('*.png')))!=8:
        raise SystemExit('Cannot skip stills: expected eight final PNGs.')
    stages=stages[1:]
    status['completed'].append('stills')
for name,script,arguments in stages:
    status['current_stage']=name
    (OUT/'review'/'pipeline_status.json').write_text(json.dumps(status,indent=2))
    print('DELIVERY_STAGE_START',name,flush=True)
    with (OUT/'logs'/f'delivery_{name}.log').open('w') as log:
        result=subprocess.run([sys.executable,str(OUT/'scripts'/script),*arguments],stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:
        status['failed_stage']=name
        status['exit_code']=result.returncode
        (OUT/'review'/'pipeline_status.json').write_text(json.dumps(status,indent=2))
        raise SystemExit(f'{name} failed; inspect delivery_{name}.log')
    status['completed'].append(name)
    print('DELIVERY_STAGE_DONE',name,flush=True)
status['current_stage']='complete'
status['finished_utc']=datetime.now(timezone.utc).isoformat()
(OUT/'review'/'pipeline_status.json').write_text(json.dumps(status,indent=2))
print('DELIVERY_RENDER_PIPELINE_COMPLETE',flush=True)
