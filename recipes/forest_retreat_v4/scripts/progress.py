"""Compact progress from completed-render receipts, never partially written PNGs."""
import json
import statistics
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent


def receipts(folder):
    rows=[]
    for path in folder.glob('render_gpu_*.jsonl'):
        for line in path.read_text().splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return {r['file']:r for r in rows}


def main():
    rows=receipts(OUT/'frames')
    stills=receipts(OUT/'renders')
    frames={r['frame'] for r in rows.values()}
    plan=json.loads((OUT/'review/shot_plan.json').read_text())
    complete=[shot['id'] for shot in plan if all(f in frames for f in range(shot['frames'][0],shot['frames'][1]+1))]
    duration=statistics.median(r['seconds'] for r in rows.values()) if rows else None
    result=dict(native_frames=len(rows),native_target=1008,stills=len(stills),stills_target=9,
                completed_shots=complete,median_frame_seconds=round(duration,2) if duration else None,
                status=json.loads((OUT/'review/production_status.json').read_text()))
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    main()
