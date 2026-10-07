"""Combine a master-matched opening with the unchanged v7 ProRes body."""
import argparse
import json
import shutil
import subprocess
from datetime import datetime,timezone

from edit import OUT,SOURCE,NATIVE_TAG,FPS,INTRO_FRAMES,OVERLAP_FRAMES,FINAL_FRAMES,DURATION

FFMPEG=shutil.which('ffmpeg')
SOURCE_MASTER=SOURCE/'Golden_Hour_Forest_Retreat_v7_ProRes_HQ.mov'
COLOR=['-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv']


def run(args,log):
    print(log,flush=True)
    with (OUT/'logs'/log).open('w') as handle:
        subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-n',*args],
            stdout=handle,stderr=subprocess.STDOUT,check=True,timeout=1800)


def main():
    p=argparse.ArgumentParser();p.add_argument('--pilot');args=p.parse_args()
    tag=args.pilot or NATIVE_TAG
    folder=OUT/'frames'/tag
    for f in range(1,INTRO_FRAMES+1):assert (folder/f'frame_{f:04d}.png').exists()
    intro=OUT/'review'/f'{tag}_intro_ProRes.mov'
    def status(stage,state='running'):
        if not args.pilot:
            (OUT/'review/production_status.json').write_text(json.dumps(dict(stage=stage,status=state,
                time_utc=datetime.now(timezone.utc).isoformat()),indent=2))
    status('intro_master')
    run(['-framerate','24','-start_number','1','-i',str(folder/'frame_%04d.png'),
         '-frames:v','96','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv422p10le',
         '-an','-c:v','prores_ks','-profile:v','3','-threads','16',*COLOR,
         '-movflags','+write_colr+faststart',str(intro)],tag+'_intro_master.log')
    if args.pilot:
        filters='[0:v]scale=720:720:in_range=tv:out_range=tv:in_color_matrix=bt709:out_color_matrix=bt709,format=yuv420p,setsar=1[intro];'
        filters+='[1:v]trim=duration=6,setpts=PTS-STARTPTS,scale=720:720:flags=lanczos:in_range=tv:out_range=tv:in_color_matrix=bt709:out_color_matrix=bt709,format=yuv420p,setsar=1[body];'
        filters+='[intro][body]concat=n=2:v=1:a=0[v]'
        run(['-i',str(intro),'-ss','1','-i',str(SOURCE_MASTER),'-filter_complex',filters,
             '-map','[v]','-an','-frames:v','240','-r','24','-c:v','libx264','-crf','17','-preset','medium',
             '-threads','12',*COLOR,'-movflags','+faststart',str(OUT/f'Golden_Hour_Forest_Retreat_v8_{tag}.mp4')],tag+'_encode.log')
        return
    tail=OUT/'review/v7_preserved_body.mov'
    master=OUT/'Golden_Hour_Forest_Retreat_v8_ProRes_HQ.mov'
    status('preserve_body')
    run(['-ss','1','-i',str(SOURCE_MASTER),'-map','0:v:0','-an','-c:v','copy','-frames:v','1320',
         '-movflags','+faststart',str(tail)],'preserve_body.log')
    listing=OUT/'review/master_concat.txt'
    listing.write_text("file '"+str(intro)+"'\nfile '"+str(tail)+"'\n")
    status('master')
    run(['-f','concat','-safe','0','-i',str(listing),'-map','0:v:0','-an','-c:v','copy',
         '-frames:v',str(FINAL_FRAMES),*COLOR,'-movflags','+write_colr+faststart',
         '-metadata','title=Golden Hour Companion - v8 player opening',str(master)],'master_concat.log')
    for resolution,crf,suffix in ((2160,'15','2160'),(1080,'18','1080_preview')):
        status('encode_'+suffix)
        run(['-i',str(master),'-map','0:v:0','-an','-frames:v',str(FINAL_FRAMES),
             '-vf',f'scale={resolution}:{resolution}:flags=lanczos:in_range=tv:out_range=tv:in_color_matrix=bt709:out_color_matrix=bt709,format=yuv420p',
             '-c:v','libx264','-preset','slow','-crf',crf,'-threads','16',*COLOR,
             '-movflags','+faststart','-metadata','title=Golden Hour Companion - v8 player opening',
             str(OUT/f'Golden_Hour_Forest_Retreat_v8_{suffix}.mp4')],suffix+'_encode.log')
    status('delivery','encoded_pending_verification')
    print('V8_ENCODED',DURATION,FINAL_FRAMES,flush=True)


if __name__=='__main__':main()
