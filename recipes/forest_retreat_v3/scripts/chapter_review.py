"""Review complete native shot segments while the rest of the film renders."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser()
parser.add_argument('--start',type=int,required=True)
parser.add_argument('--end',type=int,required=True)
parser.add_argument('--name',required=True)
args=parser.parse_args()
if args.start==1:
    for frame in range(2,49):
        target=OUT/'frames'/('frame_%04d.png'%frame)
        if not target.exists():shutil.copyfile(OUT/'frames/frame_0001.png',target)
missing=[f for f in range(args.start,args.end+1) if not (OUT/'frames'/('frame_%04d.png'%f)).exists()]
if missing:raise RuntimeError('Shot not complete: '+str(missing))
directory=OUT/'review'/'chapters'
directory.mkdir(exist_ok=True)
ffmpeg=shutil.which('ffmpeg') or 'ffmpeg'
subprocess.run([ffmpeg,'-hide_banner','-v','error','-y','-framerate','24','-start_number',str(args.start),
                '-i',str(OUT/'frames/frame_%04d.png'),'-frames:v',str(args.end-args.start+1),
                '-vf','scale=720:720:flags=lanczos','-c:v','libx264','-crf','18','-preset','fast',
                '-threads','6','-pix_fmt','yuv420p','-movflags','+faststart',
                str(directory/(args.name+'.mp4'))],check=True,timeout=300)
frames=sorted(set(range(args.start,args.end+1,12))|{args.end})
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
size=360
canvas=Image.new('RGB',(4*size,((len(frames)+3)//4)*(size+26)),'#191c1b')
draw=ImageDraw.Draw(canvas)
for i,frame in enumerate(frames):
    x,y=(i%4)*size,(i//4)*(size+26)
    draw.text((x+8,y+5),'%04d / %.2f s'%(frame,(frame-1)/24),font=font,fill='#ded6c4')
    with Image.open(OUT/'frames'/('frame_%04d.png'%frame)) as im:
        canvas.paste(im.convert('RGB').resize((size,size),Image.Resampling.LANCZOS),(x,y+26))
canvas.save(directory/(args.name+'.jpg'),quality=94)
print('CHAPTER_READY',args.name,args.start,args.end,flush=True)
