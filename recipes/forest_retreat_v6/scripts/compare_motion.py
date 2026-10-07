"""Summarise visible-motion changes against the frozen v5 film measurements."""
import argparse
import json
import statistics
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent
MATCHES={'01':'01','02':'03','04':'04','05':'05','06':'06','08':'02','09':'07','10':'08','11':'09'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--candidate',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    old=json.loads((OUT/'review/baseline_motion.json').read_text())
    new=json.loads(Path(args.candidate).read_text())
    base={s['id']:s for s in old['shots']}
    rows=[]
    for s in new['shots']:
        previous=base.get(MATCHES.get(s['id']))
        rows.append(dict(id=s['id'],name=s['name'],seconds=s['seconds'],
            median_width_percent_per_second=100*s['median'],p80_width_percent_per_second=100*s['p80'],
            previous_id=previous['id'] if previous else None,
            median_ratio_to_previous=s['median']/previous['median'] if previous else None))
    old_middle=statistics.median(s['median'] for s in old['shots'][1:-1])
    new_middle=statistics.median(s['median'] for s in new['shots'][1:-1])
    result=dict(baseline_movie=old['movie'],candidate_movie=new['movie'],candidate_frames=new['frames'],
        opening_motion_reduction_fraction=1-new['shots'][0]['median']/old['shots'][0]['median'],
        baseline_opening_to_middle_ratio=old['shots'][0]['median']/old_middle,
        candidate_opening_to_middle_ratio=new['shots'][0]['median']/new_middle,
        baseline_median_speed_spread=max(s['median'] for s in old['shots'])/min(s['median'] for s in old['shots']),
        candidate_median_speed_spread=max(s['median'] for s in new['shots'])/min(s['median'] for s in new['shots']),
        baseline_p80_speed_spread=max(s['p80'] for s in old['shots'])/min(s['p80'] for s in old['shots']),
        candidate_p80_speed_spread=max(s['p80'] for s in new['shots'])/min(s['p80'] for s in new['shots']),
        baseline_durations=[s['seconds'] for s in old['shots']],candidate_durations=[s['seconds'] for s in new['shots']],
        shots=rows,scope='Same 320px optical-flow method; visible motion includes water, foliage and parallax. Read alongside the film.')
    Path(args.output).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
