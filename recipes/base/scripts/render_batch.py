"""Schedule independent Cycles processes on explicitly chosen free GPUs."""
import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE.parent


def worker(gpu,frames,samples):
    env=os.environ.copy()
    env['GH_GPU']=str(gpu)
    env['OMP_NUM_THREADS']='8'
    log=OUT/'logs'/f'animation_gpu_{gpu}.log'
    command=['blender','-b',str(OUT/'golden_hour_companion.blend'),'-t','8',
             '--python',str(HERE/'render_scene.py'),'--','--frames',','.join(map(str,frames)),
             '--samples',str(samples),'--threshold','.015','--resolution','2160',
             '--output',str(OUT/'frames'),'--gpu-denoise','--skip-existing']
    with log.open('w') as handle:
        code=subprocess.call(command,stdout=handle,stderr=subprocess.STDOUT,env=env)
    return {'gpu':gpu,'code':code,'assigned':len(frames),'log':str(log)}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--gpus',default='1,2,3,4,5,6,7')
    p.add_argument('--samples',type=int,default=192)
    args=p.parse_args()
    gpus=[int(x) for x in args.gpus.split(',')]
    frames=[1]+list(range(49,865))
    frames=[f for f in frames if not (OUT/'frames'/f'frame_{f:04d}.png').exists()]
    groups=[frames[i::len(gpus)] for i in range(len(gpus))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(gpus)) as executor:
        jobs=[executor.submit(worker,gpu,group,args.samples) for gpu,group in zip(gpus,groups) if group]
        results=[job.result() for job in jobs]
    (OUT/'review'/'batch_status.json').write_text(json.dumps(results,indent=2))
    for result in results:
        print(json.dumps(result),flush=True)
    if any(x['code'] for x in results):
        raise SystemExit('Render worker failed; inspect logs and resume with the same command.')
    import shutil
    for f in range(2,49):
        shutil.copyfile(OUT/'frames'/'frame_0001.png',OUT/'frames'/f'frame_{f:04d}.png')
    missing=[f for f in range(1,865) if not (OUT/'frames'/f'frame_{f:04d}.png').exists()]
    if missing:
        raise SystemExit(f'Missing native frames: {missing}')
    print('ALL_864_NATIVE_FRAMES_COMPLETE',flush=True)


if __name__=='__main__':
    main()
