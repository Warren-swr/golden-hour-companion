"""Assemble native Cycles frames with restrained half-second editorial dissolves."""
import subprocess
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent


def main():
    command=['ffmpeg','-hide_banner','-y','-filter_complex_threads','4']
    for start,length in [(1,12),(289,6),(433,8),(625,10)]:
        command += ['-thread_queue_size','8','-framerate','24','-start_number',str(start),
                    '-t',str(length),'-i',str(OUT/'frames'/'frame_%04d.png')]
    graph=('[0:v]settb=AVTB,setpts=PTS-STARTPTS,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[a];'
           '[1:v]settb=AVTB,setpts=PTS-STARTPTS,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[b];'
           '[2:v]settb=AVTB,setpts=PTS-STARTPTS,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[c];'
           '[3:v]settb=AVTB,setpts=PTS-STARTPTS,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[d];'
           '[a][b]xfade=transition=fade:duration=0.5:offset=11.5[ab];'
           '[ab][c]xfade=transition=fade:duration=0.5:offset=17.0[abc];'
           '[abc][d]xfade=transition=fade:duration=0.5:offset=24.5[v]')
    command += ['-filter_complex',graph,'-map','[v]','-an','-r','24','-c:v','libx264',
                '-preset','slow','-crf','16','-pix_fmt','yuv420p','-threads','12',
                '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',
                '-movflags','+faststart','-metadata','title=Golden Hour Companion',
                '-metadata','comment=Native 2160x2160 Cycles rendering; original procedural 3D assets.',
                str(OUT/'Golden_Hour_Companion_2160.mp4')]
    subprocess.run(command,check=True)


if __name__=='__main__':
    main()
