"""Compare the revised edit to v6 at matching render quality."""
import argparse
import json
import statistics
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent
MATCHES={'01':['01'],'02':['02','03'],'03':['04'],'04':['05'],'05':['06','07'],
         '06':['08'],'07':['09'],'08':['10'],'09':['11']}


def median(rows,key):
    return statistics.median(row[key] for row in rows)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--baseline',default=str(OUT/'review/baseline_motion.json'))
    p.add_argument('--candidate',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    old=json.loads(Path(args.baseline).read_text())
    new=json.loads(Path(args.candidate).read_text())
    rows=[]
    for shot in new['shots']:
        source_ids=MATCHES[shot['id']]
        baseline=[row for row in old['per_frame'] if row['shot'] in source_ids]
        previous={key:median(baseline,key) for key in ('median','p80')}
        rows.append(dict(id=shot['id'],name=shot['name'],seconds=shot['seconds'],baseline_ids=source_ids,
            median_width_percent_per_second=100*shot['median'],p80_width_percent_per_second=100*shot['p80'],
            baseline_median_width_percent_per_second=100*previous['median'],
            baseline_p80_width_percent_per_second=100*previous['p80'],
            median_ratio_to_previous=shot['median']/previous['median'],p80_ratio_to_previous=shot['p80']/previous['p80']))
    old_all={key:median(old['per_frame'],key) for key in ('median','p80')}
    new_all={key:median(new['per_frame'],key) for key in ('median','p80')}
    result=dict(baseline_movie=old['movie'],candidate_movie=new['movie'],candidate_frames=new['frames'],
        overall_median_motion_ratio=new_all['median']/old_all['median'],
        overall_p80_motion_ratio=new_all['p80']/old_all['p80'],
        opening_median_motion_ratio=rows[0]['median_ratio_to_previous'],
        opening_p80_motion_ratio=rows[0]['p80_ratio_to_previous'],
        baseline_p80_speed_spread=max(s['p80'] for s in old['shots'])/min(s['p80'] for s in old['shots']),
        candidate_p80_speed_spread=max(s['p80'] for s in new['shots'])/min(s['p80'] for s in new['shots']),
        baseline_durations=[s['seconds'] for s in old['shots']],candidate_durations=[s['seconds'] for s in new['shots']],
        shots=rows,scope='Same 320px optical-flow method. Overall ratios use all measured frames; merged shots compare with both previous segments. Includes water, foliage and parallax.')
    Path(args.output).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
