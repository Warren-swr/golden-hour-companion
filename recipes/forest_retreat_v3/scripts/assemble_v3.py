"""Encode the v3 film from native Cycles frames: straight cuts, 0.75 s closing fade."""
import argparse
import shutil
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
FFMPEG = shutil.which('ffmpeg') or 'ffmpeg'
FRAMES, FADE = 1056, 18


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frames', default='frames')
    parser.add_argument('--movie', default='Golden_Hour_Forest_Retreat_v3_2160.mp4')
    parser.add_argument('--crf', default='15')
    parser.add_argument('--preview', help='also write a 1080 downscale to this name')
    args = parser.parse_args()
    frames = OUT / args.frames
    # The two-second opening hold repeats the single rendered reference frame.
    for frame in range(2, 49):
        dest = frames / ('frame_%04d.png' % frame)
        if not dest.exists():
            shutil.copyfile(frames / 'frame_0001.png', dest)
    missing = [f for f in range(1, FRAMES + 1) if not (frames / ('frame_%04d.png' % f)).exists()]
    if missing:
        raise RuntimeError('Missing frames: %s' % missing[:20])
    movie = OUT / args.movie
    fade = 'fade=t=out:st=%.4f:d=%.4f' % ((FRAMES - FADE) / 24, FADE / 24)
    command = [FFMPEG, '-hide_banner', '-loglevel', 'error', '-y', '-framerate', '24', '-start_number', '1',
               '-i', str(frames / 'frame_%04d.png'), '-frames:v', str(FRAMES),
               '-vf', fade + ',scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p',
               '-c:v', 'libx264', '-preset', 'slow', '-crf', args.crf, '-threads', '16',
               '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
               '-color_range', 'tv', '-movflags', '+faststart',
               '-metadata', 'title=Golden Hour Companion - A Forest Retreat (v3)',
               '-metadata', 'comment=Native Cycles square frames / 24 fps / 6 real 3D camera moves', str(movie)]
    subprocess.run(command, check=True, timeout=3600)
    if args.preview:
        subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(movie),
                        '-vf', 'scale=1080:1080:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow',
                        '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                        str(OUT / args.preview)], check=True, timeout=1800)
    print('V3_FILM_ASSEMBLED', movie, flush=True)


if __name__ == '__main__':
    main()
