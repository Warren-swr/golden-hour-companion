"""Cycles/OptiX rendering of stills or native 2160-square animation frames."""
import argparse
import bpy
import json
import os
import sys
import time
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--frames',default='1')
    parser.add_argument('--camera')
    parser.add_argument('--output',required=True)
    parser.add_argument('--resolution',type=int,default=2160)
    parser.add_argument('--samples',type=int,default=128)
    parser.add_argument('--threshold',type=float,default=.015)
    parser.add_argument('--skip-existing',action='store_true')
    parser.add_argument('--gpu-denoise',action='store_true')
    parser.add_argument('--gpu',type=int,default=int(os.environ.get('GH_GPU','0')))
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX'
    prefs.get_devices()
    devices=[]
    optix=[d for d in prefs.devices if d.type=='OPTIX']
    for d in prefs.devices:
        d.use=d==optix[args.gpu]
        if d.use:
            devices.append(d.name)
    if not devices:
        raise RuntimeError('No OptiX GPU detected; refusing an unverified software fallback.')
    sc=bpy.context.scene
    if args.camera:
        sc.timeline_markers.clear()
    sc.render.engine='CYCLES'
    sc.cycles.device='GPU'
    sc.cycles.samples=args.samples
    sc.cycles.adaptive_threshold=args.threshold
    sc.cycles.use_denoising=True
    sc.cycles.denoising_use_gpu=args.gpu_denoise
    sc.cycles.use_auto_tile=False
    sc.render.resolution_x=args.resolution
    sc.render.resolution_y=args.resolution
    sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG'
    sc.render.image_settings.color_mode='RGB'
    sc.render.image_settings.color_depth='8'
    sc.render.threads_mode='FIXED'
    sc.render.threads=8
    frames=[]
    for token in args.frames.split(','):
        if ':' in token:
            parts=[int(x) for x in token.split(':')]
            frames.extend(range(parts[0],parts[1]+1,parts[2] if len(parts)>2 else 1))
        else:
            frames.append(int(token))
    dest=Path(args.output).resolve()
    dest.parent.mkdir(parents=True,exist_ok=True)
    print('RENDER_DEVICE',json.dumps({'devices':devices,'native_resolution':args.resolution,
          'samples':args.samples,'threshold':args.threshold}),flush=True)
    for frame in frames:
        if len(frames)==1 and dest.suffix.lower()=='.png':
            target=dest
        else:
            target=dest/f'frame_{frame:04d}.png'
            dest.mkdir(parents=True,exist_ok=True)
        if args.skip_existing and target.exists():
            continue
        sc.frame_set(frame)
        if args.camera:
            sc.camera=bpy.data.objects[args.camera]
        sc.render.filepath=str(target)
        start=time.monotonic()
        bpy.ops.render.render(write_still=True)
        record={'frame':frame,'camera':sc.camera.name,'seconds':round(time.monotonic()-start,3),
                'width':args.resolution,'height':args.resolution,'samples':args.samples,'devices':devices,
                'gpu_index':args.gpu,'device_id':optix[args.gpu].id,
                'denoiser':'OPENIMAGEDENOISE','denoiser_quality':sc.cycles.denoising_quality,
                'gpu_denoising':sc.cycles.denoising_use_gpu,
                'file':str(target),'bytes':target.stat().st_size}
        with (target.parent/'render_records.jsonl').open('a') as handle:
            handle.write(json.dumps(record)+'\n')
        print('RENDER_COMPLETE',json.dumps(record),flush=True)


if __name__=='__main__':
    main()
