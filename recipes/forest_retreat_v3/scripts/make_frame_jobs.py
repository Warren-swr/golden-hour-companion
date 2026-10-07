"""Write a frame job list: frame 1 plus every moving frame (2-48 repeat frame 1)."""
import argparse
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--frames', help='comma list of a-b ranges; default whole film')
args = parser.parse_args()
frames = [1] + list(range(49, 1057))
if args.frames:
    wanted = set()
    for part in args.frames.split(','):
        a, _, b = part.partition('-')
        wanted.update(range(int(a), int(b or a) + 1))
    frames = [f for f in frames if f in wanted]
target = (OUT / args.dir).resolve()
jobs = [dict(frame=f, file=str(target / ('frame_%04d.png' % f))) for f in frames]
Path(args.out).write_text(json.dumps(jobs, indent=1))
print('FRAME_JOBS', len(jobs), target)
