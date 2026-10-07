"""Encode native 24 fps frames, with no opening duplicates or interpolation."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent
FFMPEG=shutil.which('ffmpeg')
from film import FRAMES,FPS,DURATION,SHOT_COUNT,FADE_SECONDS


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--frames',default='frames')
    p.add_argument('--movie',default='Golden_Hour_Forest_Retreat_v7_2160.mp4')
    p.add_argument('--preview')
    p.add_argument('--master')
    p.add_argument('--crf',default='15')
    args=p.parse_args()
    folder=OUT/args.frames
    missing=[f for f in range(1,FRAMES+1) if not (folder/('frame_%04d.png'%f)).exists()]
    if missing:
        raise RuntimeError('Missing native frames: %s'%missing[:25])
    command=[FFMPEG,'-hide_banner','-loglevel','error','-y','-framerate','24','-start_number','1',
             '-i',str(folder/'frame_%04d.png'),'-frames:v',str(FRAMES),
             '-vf',f'fade=t=out:st={DURATION-FADE_SECONDS}:d={FADE_SECONDS},scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p',
             '-c:v','libx264','-preset','slow','-crf',args.crf,'-threads','16',
             '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv',
             '-movflags','+faststart','-metadata','title=Golden Hour Companion - A Forest Retreat v7',
             '-metadata',f'comment={FRAMES} native Cycles frames / {FPS} fps / {SHOT_COUNT} authored camera moves',str(OUT/args.movie)]
    subprocess.run(command,check=True,timeout=3600)
    if args.master:
        subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-framerate','24','-start_number','1',
                        '-i',str(folder/'frame_%04d.png'),'-frames:v',str(FRAMES),
                        '-vf',f'fade=t=out:st={DURATION-FADE_SECONDS}:d={FADE_SECONDS},scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv422p10le',
                        '-c:v','prores_ks','-profile:v','3','-threads','16',
                        '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',
                        '-metadata','title=A Forest Retreat v7 - ProRes 422 HQ',
                        str(OUT/args.master)],check=True,timeout=3600)
    if args.preview:
        subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-i',str(OUT/args.movie),
                        '-vf','scale=1080:1080:flags=lanczos','-c:v','libx264','-preset','slow',
                        '-crf','18','-pix_fmt','yuv420p','-threads','12','-movflags','+faststart',
                        str(OUT/args.preview)],check=True,timeout=1800)
    print('V7_FILM_ASSEMBLED',OUT/args.movie,flush=True)


if __name__=='__main__':
    main()
