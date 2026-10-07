"""Contact sheets of actual Cycles samples, without altering rendered content."""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent


def main():
    p = argparse.ArgumentParser()
    p.add_argument('folder')
    p.add_argument('--columns',type=int,default=3)
    p.add_argument('--width',type=int,default=384)
    p.add_argument('--every',type=int,default=1)
    args = p.parse_args()
    files = sorted((OUT / args.folder).glob('frame_*.png'))[::args.every]
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
    for page,start in enumerate(range(0,len(files),18),1):
        items=files[start:start+18]
        h=args.width+30
        canvas=Image.new('RGB',(args.columns*args.width,math.ceil(len(items)/args.columns)*h),'#202220')
        draw=ImageDraw.Draw(canvas)
        for i,path in enumerate(items):
            frame=int(path.stem.split('_')[-1])
            x,y=(i%args.columns)*args.width,(i//args.columns)*h
            with Image.open(path) as im:
                canvas.paste(im.resize((args.width,args.width),Image.Resampling.LANCZOS),(x,y+30))
            draw.text((x+8,y+6),'Frame %04d / %.2f s'%(frame,(frame-1)/24),font=font,fill='#d9d4c6')
        dest=OUT/'review'/('%s_contact_%02d.jpg'%(Path(args.folder).name,page))
        canvas.save(dest,quality=94)
        print(dest)


if __name__=='__main__':
    main()
