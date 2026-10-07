"""Encode the player and film from one consistent original-PNG sequence."""
import argparse
import json
import shutil
import subprocess
from datetime import datetime,timezone

from edit import OUT,SOURCE,FPS,INTRO_FRAMES,OVERLAP_FRAMES,FINAL_FRAMES,DURATION

FFMPEG=shutil.which('ffmpeg')
MASTER=SOURCE/'Golden_Hour_Forest_Retreat_v7_ProRes_HQ.mov'
COLOR=['-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv']


def run(args,log):
    print(log,flush=True)
    with (OUT/'logs'/log).open('w') as handle:
        subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-n',*args],
            stdout=handle,stderr=subprocess.STDOUT,check=True,timeout=1800)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pilot')
    args=p.parse_args()
    if args.pilot:
        folder=OUT/'frames'/args.pilot
        for frame in range(1,INTRO_FRAMES+1):assert (folder/f'frame_{frame:04d}.png').exists()
        filters='[0:v]scale=720:720:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p,setsar=1[intro];'
        filters+='[1:v]trim=duration=6,setpts=PTS-STARTPTS,scale=720:720:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p,setsar=1[body];'
        filters+='[intro][body]concat=n=2:v=1:a=0[v]'
        run(['-framerate','24','-start_number','1','-i',str(folder/'frame_%04d.png'),
             '-framerate','24','-start_number','25','-t','6','-i',str(SOURCE/'frames/frame_%04d.png'),'-filter_complex',filters,
             '-map','[v]','-an','-frames:v','240','-r','24','-c:v','libx264','-crf','17','-preset','medium',
             '-threads','12',*COLOR,'-movflags','+faststart',str(OUT/f'Golden_Hour_Forest_Retreat_v8_{args.pilot}.mp4')],args.pilot+'_encode.log')
        return
    folder=OUT/'frames/native'
    for frame in range(1,INTRO_FRAMES+1):assert (folder/f'frame_{frame:04d}.png').exists()
    sequence=OUT/'frames/film'
    sequence.mkdir()
    source_hashes=json.loads((SOURCE/'review/final_frame_hashes.json').read_text())
    mapping=[]
    for frame in range(1,FINAL_FRAMES+1):
        if frame<=INTRO_FRAMES:
            original=folder/f'frame_{frame:04d}.png'
            source_frame=None
        else:
            source_frame=frame-INTRO_FRAMES+OVERLAP_FRAMES
            original=SOURCE/'frames'/f'frame_{source_frame:04d}.png'
        (sequence/f'frame_{frame:04d}.png').symlink_to(original.resolve())
        mapping.append(dict(frame=frame,source=str(original.resolve()),source_frame=source_frame,
            source_sha256=source_hashes[f'frame_{source_frame:04d}.png'] if source_frame else None))
    (OUT/'review/sequence_map.json').write_text(json.dumps(mapping,indent=2))
    dest=OUT/'Golden_Hour_Forest_Retreat_v8_ProRes_HQ.mov'
    def status(stage,state='running'):
        (OUT/'review/production_status.json').write_text(json.dumps(dict(stage=stage,status=state,
            time_utc=datetime.now(timezone.utc).isoformat()),indent=2))
    status('master')
    run(['-framerate','24','-start_number','1','-i',str(sequence/'frame_%04d.png'),
         '-frames:v',str(FINAL_FRAMES),'-vf',f'fade=t=out:st={DURATION-.75}:d=.75,scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv422p10le',
         '-an','-c:v','prores_ks','-profile:v','3','-threads','16',*COLOR,
         '-movflags','+write_colr+faststart','-metadata','title=Golden Hour Companion - v8 player opening',
         str(dest)],'master_encode.log')
    status('encode_2160')
    movie=OUT/'Golden_Hour_Forest_Retreat_v8_2160.mp4'
    run(['-framerate','24','-start_number','1','-i',str(sequence/'frame_%04d.png'),
         '-frames:v',str(FINAL_FRAMES),'-an','-vf',f'fade=t=out:st={DURATION-.75}:d=.75,scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p',
         '-c:v','libx264','-preset','slow','-crf','15','-threads','16',*COLOR,
         '-movflags','+faststart','-metadata','title=Golden Hour Companion - v8 player opening',str(movie)],'2160_encode.log')
    status('encode_1080_preview')
    run(['-i',str(movie),'-map','0:v:0','-an','-frames:v',str(FINAL_FRAMES),
         '-vf','scale=1080:1080:flags=lanczos','-c:v','libx264','-preset','slow','-crf','18','-threads','12',*COLOR,
         '-movflags','+faststart',str(OUT/'Golden_Hour_Forest_Retreat_v8_1080_preview.mp4')],'1080_preview_encode.log')
    status('delivery','encoded_pending_verification')
    print('V8_ENCODED',DURATION,FINAL_FRAMES,flush=True)


if __name__=='__main__':main()
