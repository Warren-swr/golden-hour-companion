"""Encode a numbered RGB PNG sequence directly to MP4 and a smaller preview."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames',
        '-show_streams','-show_format','-of','json',str(path)],text=True))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',required=True,help='PNG sequence pattern, for example work/frames/frame_%%04d.png')
    parser.add_argument('--frames',type=int,required=True)
    parser.add_argument('--start',type=int,default=1)
    parser.add_argument('--fps',type=int,default=24)
    parser.add_argument('--resolution',type=int,default=2160)
    parser.add_argument('--preview-resolution',type=int,default=1080)
    parser.add_argument('--output',type=Path,default=Path('work/video'))
    parser.add_argument('--name',default='golden_hour')
    args=parser.parse_args()
    if not args.name.replace('_','').replace('-','').isalnum():parser.error('Use a simple output name.')
    if min(args.frames,args.start,args.fps,args.resolution,args.preview_resolution)<1:
        parser.error('Frame counts, frame rate and dimensions must be positive.')
    if args.resolution%2 or args.preview_resolution%2 or args.preview_resolution>args.resolution:
        parser.error('Use even dimensions with preview no larger than the main output.')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):parser.error('Install FFmpeg and ffprobe first.')
    try:
        inputs=[Path(args.input % frame) for frame in range(args.start,args.start+args.frames)]
    except (TypeError,ValueError):parser.error('Input must contain one integer frame placeholder.')
    missing=next((path for path in inputs if not path.is_file()),None)
    if missing:parser.error('Missing input frame: '+str(missing))
    first=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(inputs[0])],text=True))['streams'][0]
    if first['width']!=first['height'] or first['width']<args.resolution:
        parser.error('Expected square input frames at least as large as the requested output.')
    targets=[(args.resolution,15,'2160' if args.resolution==2160 else str(args.resolution)),
             (args.preview_resolution,18,'1080_preview' if args.preview_resolution==1080 else str(args.preview_resolution)+'_preview')]
    destinations=[args.output/f'{args.name}_{suffix}.mp4' for _,_,suffix in targets]
    report=args.output/f'{args.name}_validation.json'
    if any(path.exists() for path in [*destinations,report]):parser.error('Choose a fresh output directory or name.')
    args.output.mkdir(parents=True,exist_ok=True)
    results=[]
    for (resolution,crf,_),destination in zip(targets,destinations):
        command=['ffmpeg','-hide_banner','-v','error','-n','-framerate',str(args.fps),
            '-start_number',str(args.start),'-i',args.input,'-frames:v',str(args.frames),
            '-vf',f'scale={resolution}:{resolution}:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p',
            '-an','-c:v','libx264','-preset','slow','-crf',str(crf),'-threads','8',
            '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv',
            '-movflags','+faststart',str(destination)]
        subprocess.run(command,check=True)
        info=probe(destination);stream=info['streams'][0]
        assert len(info['streams'])==1 and stream['codec_type']=='video'
        assert int(stream['nb_read_frames'])==args.frames
        assert stream['width']==stream['height']==resolution
        assert stream['avg_frame_rate']==f'{args.fps}/1'
        assert abs(float(info['format']['duration'])-args.frames/args.fps)<.001
        with destination.open('rb') as handle:digest=hashlib.file_digest(handle,'sha256').hexdigest()
        results.append(dict(file=destination.name,bytes=destination.stat().st_size,sha256=digest,
            width=resolution,height=resolution,frames=args.frames,fps=args.fps,silent=True))
        print('MP4_VERIFIED',destination,flush=True)
    report.write_text(json.dumps(dict(outputs=results,prores_generated=False),indent=2)+'\n')


if __name__=='__main__':main()
