"""Verify completed PNGs while long-running render workers continue."""
import json
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
OUT=Path(__file__).resolve().parent.parent
status_file=OUT/'review'/'render_progress.json'
old=json.loads(status_file.read_text()) if status_file.exists() else {'verified_frames':[]}
verified=set(old['verified_frames'])
records={}
for line in (OUT/'frames'/'render_records.jsonl').read_text().splitlines():
    try:
        record=json.loads(line)
        records[record['frame']]=record
    except ValueError:
        continue
for frame in records:
    if frame in verified:
        continue
    with Image.open(OUT/'frames'/f'frame_{frame:04d}.png') as im:
        assert im.size==(2160,2160)
        im.verify()
    verified.add(frame)
stages={'A_reference_room':(1,288),'B_kitchen':(289,432),'C_window_forest':(433,624),'D_forest_home':(625,864)}
summary={'checked_utc':datetime.now(timezone.utc).isoformat(),
         'rendered':len(records),'render_required':817,'pngs_crc_verified':len(verified),
         'verified_frames':sorted(verified),
         'stages':{name:sum(lo<=x<=hi for x in records) for name,(lo,hi) in stages.items()},
         'latest_frame':max(records),'errors':[]}
status_file.write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k!='verified_frames'},indent=2))
