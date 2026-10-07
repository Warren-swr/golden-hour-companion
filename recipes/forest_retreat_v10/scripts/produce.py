"""Run the accepted opening, encoding and checks with bounded stages."""
import fcntl
import hashlib
import json
import subprocess
import sys
from datetime import datetime,timezone

from edit import OUT,NATIVE_TAG


def main():
    lock=(OUT/'review/production.lock').open('w')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    gate=json.loads((OUT/'review/production_gate.json').read_text())
    assert gate['decision']=='accepted_pilot_a'
    for name,digest in gate['scripts_sha256'].items():
        with (OUT/'scripts'/name).open('rb') as handle:assert hashlib.file_digest(handle,'sha256').hexdigest()==digest
    for item in gate['decoded_opening']:
        with (OUT/item['file']).open('rb') as handle:assert hashlib.file_digest(handle,'sha256').hexdigest()==item['sha256']
    for item in gate['fonts']:
        with (OUT/item['file']).open('rb') as handle:assert hashlib.file_digest(handle,'sha256').hexdigest()==item['sha256']
    (OUT/'review/production_input.json').write_text(json.dumps(gate,indent=2))
    stages=[('render_intro',['uv','run','--with','numpy','--with','opencv-python-headless','--with','pillow',
        'python','scripts/render_intro.py','--resolution','2160','--tag',NATIVE_TAG],1800),
        ('encode',[sys.executable,'scripts/encode_final.py'],5400),
        ('verify',['uv','run','--with','numpy','--with','pillow','python','scripts/validate_v10.py'],1800)]
    def status(stage,value):
        result=dict(stage=stage,status=value,time_utc=datetime.now(timezone.utc).isoformat())
        (OUT/'review/production_status.json').write_text(json.dumps(result,indent=2))
        print(json.dumps(result),flush=True)
    for stage,command,timeout in stages:
        status(stage,'running')
        try:
            with (OUT/'logs'/('production_'+NATIVE_TAG+'_'+stage+'.log')).open('w') as handle:
                subprocess.run(command,cwd=OUT,stdout=handle,stderr=subprocess.STDOUT,check=True,timeout=timeout)
        except BaseException:
            status(stage,'failed_preserved');raise
        status(stage,'complete')
    status('delivery','verified_pending_visual_review')


if __name__=='__main__':main()
