"""Read-only progress from durable render receipts, not process exit guesses."""
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
records = []
for folder in ('frames', 'renders'):
    for path in (OUT/folder).glob('render_gpu_*.jsonl'):
        for line in path.read_text().splitlines():
            try:
                records.append(json.loads(line))
            except ValueError:
                pass
film = [r for r in records if r['resolution'] == 2160]
stills = [r for r in records if r['resolution'] == 3240]
by_camera = {}
for record in film:
    by_camera.setdefault(record['camera'], []).append(record)
report = dict(time_utc=datetime.now(timezone.utc).isoformat(),
              film_frames_rendered=len({r['frame'] for r in film}), film_frames_to_render=1009,
              stills_rendered=len(stills), stills_to_render=8,
              median_recent_frame_seconds=round(statistics.median([r['seconds'] for r in film[-40:]]),2) if film else None,
              shots={camera:dict(frames=len(rows), median_seconds=round(statistics.median(r['seconds'] for r in rows),2))
                     for camera,rows in sorted(by_camera.items())})
print(json.dumps(report, indent=2))
