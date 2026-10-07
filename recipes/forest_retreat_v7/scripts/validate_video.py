"""Decode the whole movie, inspect temporal continuity, and retain contact sheets."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parent.parent
FFMPEG=shutil.which('ffmpeg')
FFPROBE=shutil.which('ffprobe')
from film import FRAMES,FPS,DURATION,CUTS,SHOT_COUNT,FADE_SECONDS


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--movie',default='Golden_Hour_Forest_Retreat_v7_2160.mp4')
    p.add_argument('--frames',default='frames')
    p.add_argument('--resolution',type=int,default=2160)
    p.add_argument('--tag',default='final')
    args=p.parse_args()
    movie=OUT/args.movie
    probe=json.loads(subprocess.check_output([FFPROBE,'-v','error','-show_streams','-show_format','-of','json',str(movie)],text=True))
    stream=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert (stream['width'],stream['height'])==(args.resolution,args.resolution)
    assert stream['avg_frame_rate']=='24/1'
    assert abs(float(probe['format']['duration'])-DURATION)<.01
    hashes=[]
    for f in range(1,FRAMES+1):
        path=OUT/args.frames/('frame_%04d.png'%f)
        if args.resolution==2160:
            with path.open('rb') as handle:
                assert handle.read(25)[24]==16,'Final native source must retain 16-bit channels'
        with Image.open(path) as im:
            assert im.size==(args.resolution,args.resolution)
            im.verify()
        hashes.append(hashlib.file_digest(path.open('rb'),'sha256').hexdigest())
    duplicates=[i+1 for i in range(1,len(hashes)) if hashes[i]==hashes[i-1]]
    assert not duplicates, 'No duplicated hold frames are permitted'
    (OUT/'review'/('%s_frame_hashes.json'%args.tag)).write_text(json.dumps(
        {'frame_%04d.png'%(i+1):value for i,value in enumerate(hashes)},indent=2))
    dest=OUT/'review'/('%s_decoded'%args.tag)
    dest.mkdir(exist_ok=True)
    cmd=[FFMPEG,'-hide_banner','-v','error','-i',str(movie),'-vf','scale=320:320:flags=lanczos',
         '-pix_fmt','rgb24','-f','rawvideo','-']
    process=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    metrics=[]; selected=[]; previous=None; count=0; chunk=320*320*3
    sample_frames=set(range(1,FRAMES+1,12)) | CUTS | {f-1 for f in CUTS} | {FRAMES}
    while True:
        buf=bytearray()
        while len(buf)<chunk:
            block=process.stdout.read(chunk-len(buf))
            if not block:break
            buf.extend(block)
        if not buf:break
        assert len(buf)==chunk,'Truncated decoded frame'
        count+=1
        pixels=np.frombuffer(buf,dtype=np.uint8).reshape(320,320,3)
        values=pixels.astype(np.float32)/255
        delta=float(np.abs(values-previous).mean()) if previous is not None else 0
        lum=.2126*values[:,:,0]+.7152*values[:,:,1]+.0722*values[:,:,2]
        metrics.append(dict(frame=count,mean=float(lum.mean()),delta=delta,cut=count in CUTS,fade=count>FRAMES-round(FADE_SECONDS*FPS),
                            clipped_fraction=float((lum>.995).mean())))
        if count in sample_frames:
            path=dest/('frame_%04d.jpg'%count)
            Image.fromarray(pixels).save(path,quality=94)
            selected.append((count,path))
        previous=values
    error=process.stderr.read().decode(errors='replace')
    code=process.wait()
    assert code==0 and not error,error
    assert count==FRAMES,count
    black=[r['frame'] for r in metrics if r['mean']<.012 and not r['fade']]
    jumps=[r for r in metrics if r['delta']>.075 and not r['cut'] and r['frame']>1]
    assert not black,black
    assert not jumps,jumps
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
    for page,start in enumerate(range(0,len(selected),24),1):
        canvas=Image.new('RGB',(1920,1400),'#202320'); draw=ImageDraw.Draw(canvas)
        for i,(frame,path) in enumerate(selected[start:start+24]):
            x,y=i%6*320,i//6*350
            draw.text((x+6,y+5),'%.2f s / %04d'%((frame-1)/24,frame),font=font,fill='#dbd4c7')
            with Image.open(path) as im:canvas.paste(im,(x,y+30))
        canvas.save(OUT/'review'/('%s_film_contact_%02d.jpg'%(args.tag,page)),quality=94)
    master=None
    if args.resolution==2160:
        master_path=OUT/'Golden_Hour_Forest_Retreat_v7_ProRes_HQ.mov'
        master=json.loads(subprocess.check_output([FFPROBE,'-v','error','-count_frames','-select_streams','v:0',
            '-show_entries','stream=codec_name,profile,width,height,pix_fmt,nb_read_frames,avg_frame_rate,duration',
            '-of','json',str(master_path)],text=True))['streams'][0]
        assert master['codec_name']=='prores' and master['profile']=='HQ'
        assert master['pix_fmt']=='yuv422p10le' and int(master['nb_read_frames'])==FRAMES
        assert master['width']==2160 and master['height']==2160 and master['avg_frame_rate']=='24/1'
        stills=list((OUT/'renders').glob('*.png'))
        assert len(stills)==SHOT_COUNT
        for path in stills:
            with Image.open(path) as im:
                assert im.size==(3240,3240)
                im.verify()
        preview_path=OUT/'Golden_Hour_Forest_Retreat_v7_1080_preview.mp4'
        preview=json.loads(subprocess.check_output([FFPROBE,'-v','error','-count_frames','-select_streams','v:0',
            '-show_entries','stream=codec_name,width,height,pix_fmt,nb_read_frames,avg_frame_rate,duration',
            '-of','json',str(preview_path)],text=True))['streams'][0]
        assert preview['codec_name']=='h264' and preview['width']==preview['height']==1080
        assert preview['avg_frame_rate']=='24/1' and int(preview['nb_read_frames'])==FRAMES
        assert abs(float(preview['duration'])-DURATION)<.001
        (OUT/'review/preview_video_validation.json').write_text(json.dumps(dict(movie=preview_path.name,
            movie_sha256=hashlib.file_digest(preview_path.open('rb'),'sha256').hexdigest(),
            decoded_frame_count=FRAMES,stream=preview),indent=2))
    result=dict(movie=str(movie),resolution=[stream['width'],stream['height']],fps=24,frames=count,duration=DURATION,
                prores_master=master,
                movie_sha256=hashlib.file_digest(movie.open('rb'),'sha256').hexdigest(),
                decoded_every_frame=True,source_pngs_verified=FRAMES,duplicates=duplicates,black_frames=black,
                unexpected_jumps=jumps,maximum_in_shot_difference=max(r['delta'] for r in metrics if not r['cut']),
                initial_one_second_total_difference=sum(r['delta'] for r in metrics[:24]),
                limitation='Numerical integrity and contact-sheet evidence do not certify photorealism or artistic quality.')
    (OUT/'review'/('%s_video_validation.json'%args.tag)).write_text(json.dumps(result,indent=2))
    (OUT/'review'/('%s_temporal_metrics.json'%args.tag)).write_text(json.dumps(metrics))
    (OUT/'review'/('%s_ffprobe.json'%args.tag)).write_text(json.dumps(probe,indent=2))
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    main()
