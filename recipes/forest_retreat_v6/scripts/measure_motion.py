"""Measure visible motion in a decoded film, separately from world-space camera speed."""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--movie',required=True)
    parser.add_argument('--plan',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    plan=json.loads(Path(args.plan).read_text());size=320;fps=24
    process=subprocess.Popen(['ffmpeg','-hide_banner','-v','error','-i',args.movie,
        '-vf','scale=320:320:flags=lanczos','-pix_fmt','gray','-f','rawvideo','-'],
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    previous=None;frame=0;records=[]
    while True:
        data=bytearray()
        while len(data)<size*size:
            block=process.stdout.read(size*size-len(data))
            if not block:break
            data.extend(block)
        if not data:break
        assert len(data)==size*size
        frame+=1;gray=np.frombuffer(data,np.uint8).reshape(size,size)
        shot=next(s for s in plan if s['frames'][0]<=frame<=s['frames'][1])
        if previous is not None and shot['frames'][0]+6<frame<shot['frames'][1]-8:
            flow=cv2.calcOpticalFlowFarneback(previous,gray,None,.5,3,21,3,5,1.1,0)
            gx=cv2.Sobel(previous,cv2.CV_32F,1,0);gy=cv2.Sobel(previous,cv2.CV_32F,0,1)
            mask=(gx*gx+gy*gy)>144
            mask[:16,:]=False;mask[-16:,:]=False;mask[:,:16]=False;mask[:,-16:]=False
            values=flow[mask]*fps/size
            speed=np.linalg.norm(values,axis=1)
            records.append(dict(frame=frame,shot=shot['id'],median=float(np.median(speed)),
                p80=float(np.percentile(speed,80)),p95=float(np.percentile(speed,95)),
                dx=float(np.median(values[:,0])),dy=float(np.median(values[:,1]))))
        previous=gray.copy()
    error=process.stderr.read().decode();assert process.wait()==0 and not error,error
    summary=[]
    for shot in plan:
        rows=[r for r in records if r['shot']==shot['id']]
        summary.append(dict(id=shot['id'],name=shot['name'],seconds=(shot['frames'][1]-shot['frames'][0]+1)/fps,
            **{k:float(np.median([r[k] for r in rows])) for k in ('median','p80','p95','dx','dy')}))
    result=dict(movie=str(Path(args.movie).resolve()),frames=frame,units='screen widths per second',
        method='Dense optical flow on textured pixels, excluding borders and cut/fade boundary frames; includes genuine water/plant motion.',
        shots=summary,per_frame=records)
    Path(args.output).write_text(json.dumps(result,indent=2))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
