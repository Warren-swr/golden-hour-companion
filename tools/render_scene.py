"""Render a frame range from the portable scene without saving over the input."""
import argparse
import sys
from pathlib import Path

import bpy


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--start',type=int,default=1)
    parser.add_argument('--end',type=int,default=1)
    parser.add_argument('--resolution',type=int,default=720)
    parser.add_argument('--samples',type=int,default=32)
    parser.add_argument('--device',choices=['CPU','OPTIX','CUDA'],default='CPU')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    scene=bpy.context.scene
    if not scene.frame_start<=args.start<=args.end<=scene.frame_end:
        parser.error('Frame range must be within the loaded scene timeline.')
    if min(args.resolution,args.samples)<1:parser.error('Resolution and samples must be positive.')
    args.output.mkdir(parents=True,exist_ok=True)
    destinations=[args.output/f'frame_{frame:04d}.png' for frame in range(args.start,args.end+1)]
    if any(path.exists() for path in destinations):parser.error('Choose a fresh output directory or frame range.')
    scene.render.engine='CYCLES'
    scene.cycles.device='CPU' if args.device=='CPU' else 'GPU'
    if args.device!='CPU':
        preferences=bpy.context.preferences.addons['cycles'].preferences
        preferences.compute_device_type=args.device
        preferences.get_devices()
        selected=[device for device in preferences.devices if device.type==args.device]
        if not selected:parser.error('No device available for '+args.device)
        for device in preferences.devices:device.use=device in selected
    scene.cycles.samples=args.samples
    scene.cycles.use_denoising=True
    scene.render.resolution_x=scene.render.resolution_y=args.resolution
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGB'
    scene.render.image_settings.color_depth='16'
    for frame,path in zip(range(args.start,args.end+1),destinations):
        scene.frame_set(frame)
        scene.render.filepath=str(path.resolve())
        bpy.ops.render.render(write_still=True)
        print('FRAME_WRITTEN',frame,path,flush=True)


if __name__=='__main__':main()
