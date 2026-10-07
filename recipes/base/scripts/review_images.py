"""Inspection artifacts only; never used in the Blender scene or final footage."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageEnhance


def comparison(reference, render, dest):
    size=960
    ref=Image.open(reference).convert('RGB').resize((size,size),Image.Resampling.LANCZOS)
    img=Image.open(render).convert('RGB').resize((size,size),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',(size*2,size+52),(27,26,23))
    canvas.paste(ref,(0,52))
    canvas.paste(img,(size,52))
    draw=ImageDraw.Draw(canvas)
    draw.text((20,18),'REFERENCE / supplied photograph',fill=(234,221,197))
    draw.text((size+20,18),'CYCLES / fully modeled 3D reconstruction',fill=(234,221,197))
    canvas.save(str(dest)+'_side_by_side.jpg',quality=95)
    Image.blend(ref,img,.5).save(str(dest)+'_overlay_50pct.png')
    difference=ImageEnhance.Contrast(ImageChops.difference(ref,img)).enhance(1.4)
    difference.save(str(dest)+'_difference.png')


def contact_sheet(files,dest,columns=4,width=400):
    thumb_h=width+32
    canvas=Image.new('RGB',(columns*width,((len(files)+columns-1)//columns)*thumb_h),(24,24,22))
    draw=ImageDraw.Draw(canvas)
    for i,path in enumerate(files):
        im=Image.open(path).convert('RGB')
        im.thumbnail((width,width),Image.Resampling.LANCZOS)
        x,y=(i%columns)*width,(i//columns)*thumb_h
        canvas.paste(im,(x,y+32))
        draw.text((x+10,y+10),Path(path).stem,fill=(220,209,185))
    canvas.save(dest,quality=93)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--reference')
    p.add_argument('--render')
    p.add_argument('--sheet',nargs='*')
    p.add_argument('--output',required=True)
    args=p.parse_args()
    if args.sheet:
        contact_sheet(args.sheet,args.output)
    else:
        comparison(args.reference,args.render,args.output)
