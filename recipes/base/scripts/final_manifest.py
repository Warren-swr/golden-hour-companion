"""Hash final deliverables after rendering, encoding and video validation finish."""
import hashlib
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent.parent
paths=[OUT/'golden_hour_companion.blend',OUT/'Golden_Hour_Companion_2160.mp4',OUT/'README.md']
paths+=sorted((OUT/'renders').glob('*.png'))
paths+=sorted(p for p in (OUT/'covers').glob('*') if p.suffix in ('.png','.md','.json'))
paths+=sorted(p for p in (OUT/'scripts').iterdir() if p.suffix in ('.py','.sh'))
paths+=[OUT/'review'/'reference_original.jpg',OUT/'review'/'project_validation.json',
        OUT/'review'/'video_validation.json',OUT/'review'/'project_reopened_gui.png',
        OUT/'review'/'final_reference_side_by_side.jpg',OUT/'review'/'final_reference_overlay_50pct.png',
        OUT/'review'/'final_stills_contact.jpg',OUT/'review'/'final_visual_review.json',
        OUT/'review'/'forest_revision_notes.md',OUT/'review'/'camera_path.csv',
        OUT/'review'/'scene_inventory.json',OUT/'review'/'forest_before_after.jpg']
paths+=sorted((OUT/'review').glob('film_timeline_*.jpg'))
entries=[]
for path in paths:
    digest=hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda:handle.read(4*1024*1024),b''):
            digest.update(chunk)
    entries.append({'file':str(path.relative_to(OUT)),'bytes':path.stat().st_size,'sha256':digest.hexdigest()})
(OUT/'delivery_manifest.json').write_text(json.dumps({'project':'Golden Hour Companion','files':entries},indent=2))
(OUT/'SHA256SUMS.txt').write_text(''.join(x['sha256']+'  '+x['file']+'\n' for x in entries))
print('HASHED_DELIVERABLES',len(entries))
