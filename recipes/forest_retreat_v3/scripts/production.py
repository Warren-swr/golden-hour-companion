"""Single bounded, locked render job with reviewable checkpoints and no retries."""
import fcntl
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
lock = (OUT/'review/production.lock').open('w')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)


def checkpoint(stage, status):
    record = dict(stage=stage, status=status, time_utc=datetime.now(timezone.utc).isoformat())
    temp = OUT/'review/production_status.tmp'
    temp.write_text(json.dumps(record, indent=2))
    temp.replace(OUT/'review/production_status.json')
    print(json.dumps(record), flush=True)


stages = [
    ('manifests', [sys.executable, str(OUT/'scripts/prepare_delivery_jobs.py')]),
    ('rendering', [sys.executable, str(OUT/'scripts/render_jobs.py'), '--jobs', str(OUT/'review/production_all_jobs.json'),
                   '--gpus', '0,1,2,3,4,5,6,7', '--samples', '192', '--resolution', '2160',
                   '--threshold', '.013', '--dynamic', '--tag', 'production_final']),
    ('assembly', [sys.executable, str(OUT/'scripts/assemble_retreat.py')]),
]
try:
    for stage, command in stages:
        checkpoint(stage, 'running')
        with (OUT/'logs'/('production_%s.log' % stage)).open('w') as handle:
            subprocess.run(command, cwd=OUT, stdout=handle, stderr=subprocess.STDOUT, check=True, timeout=18000)
        checkpoint(stage, 'complete')
    checkpoint('render_and_encode', 'complete_pending_final_review')
except BaseException:
    checkpoint(stage, 'failed_preserved_for_review')
    raise
