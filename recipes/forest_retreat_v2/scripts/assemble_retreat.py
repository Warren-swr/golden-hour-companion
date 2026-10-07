"""Encode the 44-second film from native Cycles frames, with editorial cuts."""
import shutil
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
FFMPEG = shutil.which('ffmpeg') or 'ffmpeg'
for frame in range(2, 49):
    dest = OUT/'frames'/('frame_%04d.png' % frame)
    if not dest.exists():
        shutil.copyfile(OUT/'frames/frame_0001.png', dest)
missing = [frame for frame in range(1, 1057) if not (OUT/'frames'/('frame_%04d.png' % frame)).exists()]
if missing:
    raise RuntimeError('Missing native frames: ' + str(missing))
movie = OUT/'Golden_Hour_Forest_Retreat_2160.mp4'
command = [FFMPEG, '-hide_banner', '-y', '-threads', '12', '-framerate', '24', '-start_number', '1',
           '-i', str(OUT/'frames/frame_%04d.png'), '-frames:v', '1056',
           '-vf', 'scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-threads', '12',
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
           '-color_range', 'tv', '-movflags', '+faststart',
           '-metadata', 'title=Golden Hour Companion - A Forest Retreat',
           '-metadata', 'comment=Native Cycles 2160 square / 24fps / 8 real 3D camera moves', str(movie)]
subprocess.run(command, check=True, timeout=1800)
subprocess.run([FFMPEG, '-hide_banner', '-y', '-i', str(movie), '-vf', 'scale=1080:1080:flags=lanczos',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-threads', '12',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                str(OUT/'Golden_Hour_Forest_Retreat_1080_preview.mp4')], check=True, timeout=1200)
print('NATIVE_FILM_ASSEMBLED', movie, flush=True)
