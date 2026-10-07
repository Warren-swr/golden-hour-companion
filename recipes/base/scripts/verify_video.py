"""Decode the entire final film, audit native frames, and inspect its full timeline."""
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

OUT=Path(__file__).resolve().parent.parent
MOVIE=OUT/'Golden_Hour_Companion_2160.mp4'
REVIEW=OUT/'review'


def main():
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames',
        '-show_streams','-show_format','-of','json',str(MOVIE)]))
    stream=next(x for x in probe['streams'] if x['codec_type']=='video')
    assert (stream['width'],stream['height'])==(2160,2160)
    assert stream['avg_frame_rate']=='24/1'
    assert int(stream['nb_read_frames'])==828
    assert abs(float(probe['format']['duration'])-34.5)<.042
    subprocess.run(['ffmpeg','-hide_banner','-v','error','-xerror','-i',str(MOVIE),
                    '-map','0:v:0','-f','null','-'],check=True)
    (REVIEW/'ffprobe_final.json').write_text(json.dumps(probe,indent=2))
    # Every native source PNG is opened and its CRC is verified.
    for f in range(1,865):
        path=OUT/'frames'/f'frame_{f:04d}.png'
        with Image.open(path) as im:
            assert im.size==(2160,2160),(f,im.size)
            im.verify()
    native_hash=hashlib.sha256((OUT/'frames'/'frame_0001.png').read_bytes()).hexdigest()
    for f in range(2,49):
        assert hashlib.sha256((OUT/'frames'/f'frame_{f:04d}.png').read_bytes()).hexdigest()==native_hash
    # Analyse every decoded frame at low spatial resolution; this is QA only.
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(MOVIE),'-vf',
        'scale=64:64,format=gray','-f','rawvideo','-pix_fmt','gray','-'])
    frames=[raw[i:i+4096] for i in range(0,len(raw),4096)]
    mean=[sum(f)/4096 for f in frames]
    delta=[sum(abs(a-b) for a,b in zip(frames[i],frames[i-1]))/4096 for i in range(1,len(frames))]
    largest=sorted(enumerate(delta,start=2),key=lambda x:x[1],reverse=True)[:12]
    sheetdir=REVIEW/'video_timeline'
    sheetdir.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(MOVIE),'-vf','fps=2,scale=320:320',
                    '-q:v','2',str(sheetdir/'time_%03d.jpg')],check=True)
    photos=sorted(sheetdir.glob('time_*.jpg'))
    for page in range((len(photos)+23)//24):
        selected=photos[page*24:(page+1)*24]
        canvas=Image.new('RGB',(1280,6*351),(22,22,20))
        draw=ImageDraw.Draw(canvas)
        for i,path in enumerate(selected):
            x,y=(i%4)*320,(i//4)*351
            canvas.paste(Image.open(path).convert('RGB'),(x,y+31))
            t=(page*24+i)/2
            draw.text((x+12,y+10),f'{t:05.1f} s / final MP4',fill=(237,221,195))
        canvas.save(REVIEW/f'film_timeline_{page+1:02d}.jpg',quality=95)
    report={'file':MOVIE.name,'codec':stream['codec_name'],'native_size':[2160,2160],
            'fps':24,'duration_seconds':float(probe['format']['duration']),
            'decoded_frames':len(frames),'full_decode_exit_code':0,'source_pngs_verified':864,
            'static_opening_frames_verified':48,'entire_timeline_review_images':len(photos),
            'frame_mean_luma_range':[min(mean),max(mean)],
            'largest_adjacent_frame_luma_differences':largest,
            'unexpected_black_frames':[i+1 for i,v in enumerate(mean) if v<3],
            'large_frame_changes':[i+2 for i,v in enumerate(delta) if v>15],
            'sha256':hashlib.sha256(MOVIE.read_bytes()).hexdigest()}
    (REVIEW/'video_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':
    main()
