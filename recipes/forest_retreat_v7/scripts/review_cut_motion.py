"""Compare visible movement immediately before and after each editorial cut."""
import argparse
import json
import statistics
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--motion',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    motion=json.loads(Path(args.motion).read_text())
    cuts=[]
    window=12
    for previous,current in zip(motion['shots'],motion['shots'][1:]):
        outgoing=[r for r in motion['per_frame'] if r['shot']==previous['id']][-window:]
        incoming=[r for r in motion['per_frame'] if r['shot']==current['id']][:window]
        assert len(outgoing)==len(incoming)==window
        speeds=[100*statistics.median(r['p80'] for r in rows) for rows in (outgoing,incoming)]
        assert min(speeds)>0
        cuts.append(dict(cut=previous['id']+' to '+current['id'],
            outgoing_width_percent_s=speeds[0],incoming_width_percent_s=speeds[1],
            ratio=max(speeds)/min(speeds),
            outgoing_frames=[r['frame'] for r in outgoing],incoming_frames=[r['frame'] for r in incoming]))
    result=dict(movie=motion['movie'],frames=motion['frames'],window_frames=window,
        method='Median of per-frame textured-pixel p80 optical flow over the last and first 12 measured frames of adjacent shots. Uses the boundary exclusions recorded by measure_motion.py; not an artistic continuity score.',
        maximum_ratio=max(c['ratio'] for c in cuts),cuts=cuts)
    Path(args.output).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
